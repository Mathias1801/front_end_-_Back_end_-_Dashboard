import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_absolute_error, r2_score
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Config ─────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aurum_tempus.db")
engine       = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
MODEL_DIR    = os.path.join(os.path.dirname(__file__), "saved")
os.makedirs(MODEL_DIR, exist_ok=True)


# ── Load Analytics Tables ──────────────────────────────────────
def load_data() -> dict[str, pd.DataFrame]:
    print("Loading analytics tables...")
    with engine.connect() as conn:
        data = {
            "rfm"            : pd.read_sql("SELECT * FROM mart_rfm",             conn),
            "orders"         : pd.read_sql("SELECT * FROM fact_orders",          conn),
            "order_items"    : pd.read_sql("SELECT * FROM fact_order_items",     conn),
            "events"         : pd.read_sql("SELECT * FROM fact_events",          conn),
            "customers"      : pd.read_sql("SELECT * FROM dim_customers",        conn),
            "monthly_revenue": pd.read_sql("SELECT * FROM mart_monthly_revenue", conn),
        }
    return data


# ══════════════════════════════════════════════════════════════
# MODEL 1 — Customer Segmentation (KMeans on RFM)
# ══════════════════════════════════════════════════════════════
def train_segmentation(data: dict) -> pd.DataFrame:
    print("\n── Model 1: Customer Segmentation ──────────────────")

    rfm = data["rfm"][["customer_id", "recency", "frequency", "monetary"]].copy()
    rfm = rfm.dropna()

    # Scale features
    scaler   = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[["recency", "frequency", "monetary"]])

    # Find optimal k with inertia elbow (we'll fix at 4 for interpretability)
    k = 4
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    rfm["cluster"] = kmeans.fit_predict(rfm_scaled)

    # Label clusters by monetary mean (high → low)
    cluster_means = rfm.groupby("cluster")["monetary"].mean().sort_values(ascending=False)
    label_map     = {
        cluster_means.index[0]: "High Value",
        cluster_means.index[1]: "Mid Tier",
        cluster_means.index[2]: "Occasional",
        cluster_means.index[3]: "Dormant",
    }
    rfm["segment_label"] = rfm["cluster"].map(label_map)

    # Print summary
    summary = rfm.groupby("segment_label").agg(
        n_customers = ("customer_id", "count"),
        avg_recency = ("recency",     "mean"),
        avg_orders  = ("frequency",   "mean"),
        avg_spend   = ("monetary",    "mean"),
    ).round(1)
    print(summary.to_string())

    # Save model + scaler
    with open(os.path.join(MODEL_DIR, "segmentation_kmeans.pkl"), "wb") as f:
        pickle.dump({"model": kmeans, "scaler": scaler, "label_map": label_map}, f)

    # Write results back to DB
    with engine.begin() as conn:
        rfm.to_sql("ml_segments", conn, if_exists="replace", index=False)
    print("  Saved → ml/saved/segmentation_kmeans.pkl")
    print("  Written → ml_segments table")

    return rfm


# ══════════════════════════════════════════════════════════════
# MODEL 2 — Churn Prediction (Random Forest Classifier)
# ══════════════════════════════════════════════════════════════
def train_churn(data: dict) -> None:
    print("\n── Model 2: Churn Prediction ────────────────────────")

    rfm    = data["rfm"].copy()
    orders = pd.to_datetime(data["orders"]["created_at"])

    # Define churn: no purchase in last 365 days
    snapshot    = orders.max()
    last_order  = data["orders"].groupby("customer_id")["created_at"].max()
    last_order  = pd.to_datetime(last_order)
    churned     = ((snapshot - last_order).dt.days > 365).astype(int).reset_index()
    churned.columns = ["customer_id", "churned"]

    df = rfm.merge(churned, on="customer_id").dropna()

    features = ["recency", "frequency", "monetary", "r_score", "f_score", "m_score"]
    X = df[features]
    y = df["churned"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=["Active", "Churned"]))

    # Feature importance
    importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
    print("Feature importances:")
    print(importances.round(3).to_string())

    # Save predictions
    df["churn_probability"] = model.predict_proba(X)[:, 1]
    df["churn_prediction"]  = model.predict(X)

    with engine.begin() as conn:
        df[["customer_id", "churn_probability", "churn_prediction"]].to_sql(
            "ml_churn", conn, if_exists="replace", index=False
        )

    with open(os.path.join(MODEL_DIR, "churn_rf.pkl"), "wb") as f:
        pickle.dump(model, f)

    print("  Saved → ml/saved/churn_rf.pkl")
    print("  Written → ml_churn table")


# ══════════════════════════════════════════════════════════════
# MODEL 3 — LTV Prediction (Gradient Boosting Regressor)
# ══════════════════════════════════════════════════════════════
def train_ltv(data: dict) -> None:
    print("\n── Model 3: LTV Prediction ──────────────────────────")

    rfm      = data["rfm"].copy()
    orders   = data["orders"].copy()
    orders["created_at"] = pd.to_datetime(orders["created_at"])

    # Split history: train on first half of customer lifetime, predict total
    orders["order_rank"] = orders.groupby("customer_id")["created_at"].rank(method="first")
    total_orders         = orders.groupby("customer_id")["order_id"].count().reset_index()
    total_orders.columns = ["customer_id", "total_orders"]

    early_spend = orders[orders["order_rank"] == 1].groupby("customer_id")["total_chf"].sum().reset_index()
    early_spend.columns = ["customer_id", "first_order_value"]

    total_spend = orders.groupby("customer_id")["total_chf"].sum().reset_index()
    total_spend.columns = ["customer_id", "ltv"]

    df = rfm.merge(early_spend, on="customer_id")
    df = df.merge(total_spend,  on="customer_id")
    df = df.merge(total_orders, on="customer_id")
    df = df.dropna()

    features = ["recency", "frequency", "first_order_value", "r_score", "f_score", "m_score"]
    X = df[features]
    y = df["ltv"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"  MAE : CHF {mean_absolute_error(y_test, y_pred):,.0f}")
    print(f"  R²  : {r2_score(y_test, y_pred):.3f}")

    df["predicted_ltv"] = model.predict(X)

    with engine.begin() as conn:
        df[["customer_id", "ltv", "predicted_ltv"]].to_sql(
            "ml_ltv", conn, if_exists="replace", index=False
        )

    with open(os.path.join(MODEL_DIR, "ltv_gbr.pkl"), "wb") as f:
        pickle.dump(model, f)

    print("  Saved → ml/saved/ltv_gbr.pkl")
    print("  Written → ml_ltv table")


# ══════════════════════════════════════════════════════════════
# MODEL 4 — Product Recommendations (Collaborative Filtering)
# ══════════════════════════════════════════════════════════════
def train_recommendations(data: dict) -> None:
    print("\n── Model 4: Product Recommendations ────────────────")

    order_items = data["order_items"].copy()

    # Build customer-product matrix
    matrix = order_items.groupby(["customer_id", "product_id"])["quantity"].sum().unstack(fill_value=0)

    # Cosine similarity between products
    from sklearn.metrics.pairwise import cosine_similarity
    product_sim = pd.DataFrame(
        cosine_similarity(matrix.T),
        index   = matrix.columns,
        columns = matrix.columns,
    )

    # For each product, find top 3 similar products
    recommendations = {}
    for product_id in product_sim.columns:
        similar = (
            product_sim[product_id]
            .drop(index=product_id)
            .sort_values(ascending=False)
            .head(3)
        )
        recommendations[product_id] = similar.index.tolist()

    # Flatten to dataframe
    rows = []
    for product_id, similar_ids in recommendations.items():
        for rank, sim_id in enumerate(similar_ids, 1):
            rows.append({
                "product_id"            : product_id,
                "recommended_product_id": sim_id,
                "rank"                  : rank,
                "similarity_score"      : product_sim.loc[product_id, sim_id],
            })

    recs_df = pd.DataFrame(rows)
    print(recs_df.to_string(index=False))

    with engine.begin() as conn:
        recs_df.to_sql("ml_recommendations", conn, if_exists="replace", index=False)

    with open(os.path.join(MODEL_DIR, "recommendations.pkl"), "wb") as f:
        pickle.dump({"similarity_matrix": product_sim, "recommendations": recommendations}, f)

    print("  Saved → ml/saved/recommendations.pkl")
    print("  Written → ml_recommendations table")


# ── Run All ────────────────────────────────────────────────────
def run():
    print(f"\n{'='*50}")
    print(f"  Aurum Tempus ML Pipeline")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    data = load_data()

    train_segmentation(data)
    train_churn(data)
    train_ltv(data)
    train_recommendations(data)

    print(f"\n{'='*50}")
    print("  All models trained and saved.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run()