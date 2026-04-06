import os
import sys
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Config ─────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aurum_tempus.db")
engine       = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# ── Extract ────────────────────────────────────────────────────
def extract() -> dict[str, pd.DataFrame]:
    print("Extracting raw data...")
    with engine.connect() as conn:
        raw = {
            "customers"   : pd.read_sql("SELECT * FROM customers",   conn),
            "orders"      : pd.read_sql("SELECT * FROM orders",      conn),
            "order_items" : pd.read_sql("SELECT * FROM order_items", conn),
            "products"    : pd.read_sql("SELECT * FROM products",    conn),
            "events"      : pd.read_sql("SELECT * FROM events",      conn),
        }
    for name, df in raw.items():
        print(f"  {name}: {len(df):,} rows")
    return raw


# ── Transform ──────────────────────────────────────────────────
def transform(raw: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    print("Transforming...")

    customers   = raw["customers"].copy()
    orders      = raw["orders"].copy()
    order_items = raw["order_items"].copy()
    products    = raw["products"].copy()
    events      = raw["events"].copy()

    # Parse datetimes
    for df in [customers, orders, events]:
        for col in df.columns:
            if "created_at" in col or "at" in col:
                df[col] = pd.to_datetime(df[col], errors="coerce")

    # ── Dim: Customers ─────────────────────────────────────────
    dim_customers = customers[[
        "id", "name", "email", "country", "city", "created_at"
    ]].rename(columns={"id": "customer_id", "created_at": "first_seen_at"})
    dim_customers["country"] = dim_customers["country"].fillna("Unknown")
    dim_customers["city"]    = dim_customers["city"].fillna("Unknown")

    # ── Dim: Products ──────────────────────────────────────────
    dim_products = products[[
        "id", "name", "collection", "price_chf", "stock"
    ]].rename(columns={"id": "product_id"})

    # ── Dim: Date ──────────────────────────────────────────────
    all_dates  = pd.to_datetime(orders["created_at"]).dropna()
    date_range = pd.date_range(all_dates.min(), all_dates.max(), freq="D")
    dim_date   = pd.DataFrame({"date": date_range})
    dim_date["year"]        = dim_date["date"].dt.year
    dim_date["month"]       = dim_date["date"].dt.month
    dim_date["month_name"]  = dim_date["date"].dt.strftime("%B")
    dim_date["quarter"]     = dim_date["date"].dt.quarter
    dim_date["day_of_week"] = dim_date["date"].dt.day_name()
    dim_date["is_weekend"]  = dim_date["date"].dt.dayofweek >= 5
    dim_date["date_id"]     = dim_date["date"].dt.strftime("%Y%m%d").astype(int)

    # ── Fact: Orders ───────────────────────────────────────────
    fact_orders = orders[[
        "id", "customer_id", "status", "total_chf", "created_at"
    ]].rename(columns={"id": "order_id"})
    fact_orders["date_id"] = pd.to_datetime(fact_orders["created_at"]).dt.strftime("%Y%m%d").astype(int)
    fact_orders["year"]    = pd.to_datetime(fact_orders["created_at"]).dt.year
    fact_orders["month"]   = pd.to_datetime(fact_orders["created_at"]).dt.month

    # ── Fact: Order Items ──────────────────────────────────────
    fact_order_items = order_items.merge(
        fact_orders[["order_id", "customer_id", "date_id", "year", "month"]],
        on="order_id"
    ).merge(
        dim_products[["product_id", "name", "collection"]],
        on="product_id"
    )
    fact_order_items["revenue"] = fact_order_items["unit_price"] * fact_order_items["quantity"]

    # ── Fact: Events ───────────────────────────────────────────
    fact_events = events.copy()
    fact_events["date_id"] = pd.to_datetime(fact_events["created_at"]).dt.strftime("%Y%m%d").astype(int)
    fact_events["year"]    = pd.to_datetime(fact_events["created_at"]).dt.year
    fact_events["month"]   = pd.to_datetime(fact_events["created_at"]).dt.month
    fact_events["hour"]    = pd.to_datetime(fact_events["created_at"]).dt.hour

    # ── Mart: RFM ──────────────────────────────────────────────
    # Recency, Frequency, Monetary — the foundation for segmentation
    snapshot_date = fact_orders["created_at"].max()

    rfm = fact_orders.groupby("customer_id").agg(
        recency   = ("created_at", lambda x: (snapshot_date - x.max()).days),
        frequency = ("order_id",   "count"),
        monetary  = ("total_chf",  "sum"),
    ).reset_index()

    # Score each dimension 1–5
    rfm["r_score"] = pd.qcut(rfm["recency"],   5, labels=[5,4,3,2,1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"),  5, labels=[1,2,3,4,5]).astype(int)
    rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

    rfm["segment"] = rfm["rfm_score"].apply(rfm_segment_label)

    # ── Mart: Funnel ───────────────────────────────────────────
    funnel = fact_events.groupby("event_type")["id"].count().reset_index()
    funnel.columns = ["event_type", "count"]
    funnel["order"] = funnel["event_type"].map({
        "page_view"      : 1,
        "product_view"   : 2,
        "add_to_cart"    : 3,
        "checkout_start" : 4,
        "purchase"       : 5,
    })
    funnel = funnel.sort_values("order").reset_index(drop=True)

    # ── Mart: Monthly Revenue ──────────────────────────────────
    monthly_revenue = fact_orders.groupby(["year", "month"]).agg(
        revenue    = ("total_chf", "sum"),
        orders     = ("order_id",  "count"),
        aov        = ("total_chf", "mean"),  # average order value
    ).reset_index()
    monthly_revenue["period"] = monthly_revenue["year"].astype(str) + "-" + monthly_revenue["month"].astype(str).str.zfill(2)

    # ── Mart: Product Performance ──────────────────────────────
    product_performance = fact_order_items.groupby(["product_id", "name", "collection"]).agg(
        units_sold    = ("quantity", "sum"),
        total_revenue = ("revenue",  "sum"),
        n_orders      = ("order_id", "nunique"),
    ).reset_index()
    product_performance["avg_revenue_per_order"] = (
        product_performance["total_revenue"] / product_performance["n_orders"]
    )

    print("  Transformation complete.")
    return {
        "dim_customers"       : dim_customers,
        "dim_products"        : dim_products,
        "dim_date"            : dim_date,
        "fact_orders"         : fact_orders,
        "fact_order_items"    : fact_order_items,
        "fact_events"         : fact_events,
        "mart_rfm"            : rfm,
        "mart_funnel"         : funnel,
        "mart_monthly_revenue": monthly_revenue,
        "mart_product_perf"   : product_performance,
    }


def rfm_segment_label(score: int) -> str:
    if score >= 13: return "Champions"
    if score >= 10: return "Loyal"
    if score >= 7:  return "Potential"
    if score >= 4:  return "At Risk"
    return "Lost"


# ── Load ───────────────────────────────────────────────────────
def load(transformed: dict[str, pd.DataFrame]) -> None:
    print("Loading to analytics tables...")
    with engine.begin() as conn:
        for table_name, df in transformed.items():
            df.to_sql(
                table_name,
                conn,
                if_exists="replace",
                index=False,
            )
            print(f"  Loaded {table_name}: {len(df):,} rows")


# ── Run ────────────────────────────────────────────────────────
def run():
    print(f"\n{'='*50}")
    print(f"  Aurum Tempus ETL Pipeline")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    raw         = extract()
    transformed = transform(raw)
    load(transformed)

    print(f"\n{'='*50}")
    print("  ETL complete.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run()