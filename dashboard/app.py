import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from sqlalchemy import create_engine

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Config ─────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aurum_tempus.db")
engine       = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

st.set_page_config(
    page_title = "Aurum Tempus — Analytics",
    page_icon  = None,
    layout     = "wide",
)

# ── Styling ────────────────────────────────────────────────────
GOLD  = "#b8933f"
LIGHT = "#d4af6a"
DARK  = "#0d0a05"
BG    = "#1a1410"
TEXT  = "#f7f4ee"
MUTED = "#9a8a6a"

st.markdown("""
<style>
  [data-testid="stAppViewContainer"]  { background: #0d0a05; color: #f7f4ee; }
  [data-testid="stSidebar"]           { background: #1a1410; border-right: 1px solid #b8933f33; }
  [data-testid="metric-container"]    { background: #1a1410; border: 1px solid #b8933f33; padding: 1rem; border-radius: 2px; }
  h1, h2, h3, h4                      { color: #d4af6a; font-family: Georgia, serif; letter-spacing: 0.05em; }
  p, label, span                      { color: #f7f4ee; }
  .stTabs [data-baseweb="tab"]        { color: #9a8a6a; font-family: Georgia, serif; letter-spacing: 0.1em; text-transform: uppercase; font-size: 0.75rem; }
  .stTabs [aria-selected="true"]      { color: #d4af6a; border-bottom: 2px solid #b8933f; }
  [data-testid="stDataFrame"]         { border: 1px solid #b8933f33; }
  div[data-testid="stMetricValue"]    { color: #d4af6a; font-family: Georgia, serif; font-size: 1.8rem; }
  div[data-testid="stMetricDelta"]    { font-size: 0.75rem; }
  .stSelectbox label, .stMultiSelect label { color: #9a8a6a; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; }
  hr                                  { border-color: #b8933f33; }
</style>
""", unsafe_allow_html=True)


# ── Data Loading ───────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_table(table: str) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql(f"SELECT * FROM {table}", conn)

@st.cache_data(ttl=300)
def load_all() -> dict[str, pd.DataFrame]:
    tables = [
        "dim_customers", "dim_products",
        "fact_orders", "fact_order_items", "fact_events",
        "mart_rfm", "mart_funnel", "mart_monthly_revenue", "mart_product_perf",
        "ml_segments", "ml_churn", "ml_ltv", "ml_recommendations",
    ]
    data = {}
    for t in tables:
        try:
            data[t] = load_table(t)
        except Exception:
            data[t] = pd.DataFrame()
    return data


# ── Helpers ────────────────────────────────────────────────────
def fmt_chf(val: float) -> str:
    return f"CHF {val:,.0f}"

def base_layout(fig, title=""):
    fig.update_layout(
        title            = dict(text=title, font=dict(family="Georgia, serif", color=LIGHT, size=14)),
        paper_bgcolor    = BG,
        plot_bgcolor     = BG,
        font             = dict(color=TEXT, family="Georgia, serif", size=11),
        colorway         = [GOLD, LIGHT, "#8B6914", "#C9A84C", "#6B4F1A"],
        xaxis            = dict(gridcolor="#2a2018", linecolor="#2a2018", tickfont=dict(color=MUTED)),
        yaxis            = dict(gridcolor="#2a2018", linecolor="#2a2018", tickfont=dict(color=MUTED)),
        legend           = dict(bgcolor=BG, bordercolor="rgba(184,147,63,0.2)", borderwidth=1, font=dict(color=MUTED)),
        margin           = dict(t=50, b=40, l=50, r=20),
    )
    return fig


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### Aurum Tempus")
    st.markdown(
        "<span style='font-size:0.7rem;letter-spacing:0.2em;color:#9a8a6a;text-transform:uppercase'>"
        "Management Analytics</span>",
        unsafe_allow_html=True
    )
    st.divider()

    data = load_all()

    if not data["fact_orders"].empty:
        orders_all = data["fact_orders"].copy()
        orders_all["created_at"] = pd.to_datetime(orders_all["created_at"])
        years = sorted(orders_all["created_at"].dt.year.unique())
        selected_years = st.multiselect(
            "Year",
            options  = years,
            default  = years,
        )
    else:
        selected_years = []

    st.divider()
    st.caption("Cache refreshes every 5 minutes.")
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()


# ── Apply year filter ──────────────────────────────────────────
if not data["fact_orders"].empty and selected_years:
    orders = data["fact_orders"].copy()
    orders["created_at"] = pd.to_datetime(orders["created_at"])
    orders = orders[orders["created_at"].dt.year.isin(selected_years)]
else:
    orders = pd.DataFrame()


# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.markdown("# Aurum Tempus — Business Intelligence")
st.markdown(
    "<span style='font-size:0.75rem;letter-spacing:0.2em;color:#9a8a6a;text-transform:uppercase'>"
    "Geneva · Est. 1889</span>",
    unsafe_allow_html=True
)
st.divider()


# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab_overview, tab_products, tab_customers, tab_funnel, tab_ml = st.tabs([
    "Overview",
    "Products",
    "Customers",
    "Funnel",
    "ML Insights",
])


# ══════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
with tab_overview:

    if orders.empty:
        st.warning("No order data available for selected period.")
    else:
        # ── KPI Row ────────────────────────────────────────────
        total_revenue  = orders["total_chf"].sum()
        total_orders   = len(orders)
        aov            = orders["total_chf"].mean()
        total_customers= orders["customer_id"].nunique()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Revenue",    fmt_chf(total_revenue))
        k2.metric("Total Orders",     f"{total_orders:,}")
        k3.metric("Avg. Order Value", fmt_chf(aov))
        k4.metric("Active Customers", f"{total_customers:,}")

        st.markdown("---")

        # ── Monthly Revenue ────────────────────────────────────
        monthly = data["mart_monthly_revenue"].copy()
        monthly = monthly[monthly["year"].isin(selected_years)]
        monthly = monthly.sort_values(["year", "month"])
        monthly["label"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)

        fig_rev = go.Figure()
        for year in sorted(monthly["year"].unique()):
            yr_data = monthly[monthly["year"] == year]
            fig_rev.add_trace(go.Scatter(
                x    = yr_data["label"],
                y    = yr_data["revenue"],
                name = str(year),
                mode = "lines+markers",
                line = dict(width=2),
            ))
        base_layout(fig_rev, "Monthly Revenue — CHF")
        st.plotly_chart(fig_rev, use_container_width=True)

        # ── Revenue by Collection ──────────────────────────────
        col_left, col_right = st.columns(2)

        with col_left:
            if not data["fact_order_items"].empty:
                items = data["fact_order_items"].copy()
                items = items[items["year"].isin(selected_years)]
                by_collection = items.groupby("collection")["revenue"].sum().reset_index()

                fig_col = px.pie(
                    by_collection,
                    names  = "collection",
                    values = "revenue",
                    hole   = 0.55,
                )
                fig_col.update_traces(
                    textfont_color = TEXT,
                    marker         = dict(colors=[GOLD, LIGHT, "#8B6914", "#C9A84C", "#6B4F1A"],
                                          line=dict(color=BG, width=2))
                )
                base_layout(fig_col, "Revenue by Collection")
                st.plotly_chart(fig_col, use_container_width=True)

        with col_right:
            # Orders by status
            status_counts = orders.groupby("status")["order_id"].count().reset_index()
            status_counts.columns = ["status", "count"]

            fig_status = px.bar(
                status_counts,
                x           = "status",
                y           = "count",
                text        = "count",
            )
            fig_status.update_traces(marker_color=GOLD, textfont_color=TEXT)
            base_layout(fig_status, "Orders by Status")
            st.plotly_chart(fig_status, use_container_width=True)

        # ── Revenue by Country ─────────────────────────────────
        if not data["dim_customers"].empty:
            customers_df = data["dim_customers"].copy()
            orders_country = orders.merge(
                customers_df[["customer_id", "country"]], on="customer_id", how="left"
            )
            by_country = (
                orders_country.groupby("country")["total_chf"]
                .sum()
                .reset_index()
                .sort_values("total_chf", ascending=False)
                .head(10)
            )

            fig_country = px.bar(
                by_country,
                x           = "total_chf",
                y           = "country",
                orientation = "h",
                text        = by_country["total_chf"].apply(fmt_chf),
            )
            fig_country.update_traces(marker_color=GOLD, textfont_color=TEXT)
            base_layout(fig_country, "Revenue by Country — Top 10")
            fig_country.update_layout(yaxis=dict(autorange="reversed", gridcolor="#2a2018"))
            st.plotly_chart(fig_country, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 2 — PRODUCTS
# ══════════════════════════════════════════════════════════════
with tab_products:

    if data["mart_product_perf"].empty:
        st.warning("No product data available.")
    else:
        perf = data["mart_product_perf"].copy()

        # ── KPI Row ────────────────────────────────────────────
        p1, p2, p3 = st.columns(3)
        p1.metric("Total Units Sold",    f"{perf['units_sold'].sum():,}")
        p2.metric("Total Revenue",       fmt_chf(perf["total_revenue"].sum()))
        p3.metric("Best Performing",     perf.loc[perf["total_revenue"].idxmax(), "name"])

        st.markdown("---")

        col_l, col_r = st.columns(2)

        with col_l:
            fig_units = px.bar(
                perf.sort_values("units_sold", ascending=True),
                x           = "units_sold",
                y           = "name",
                orientation = "h",
                text        = "units_sold",
            )
            fig_units.update_traces(marker_color=GOLD, textfont_color=TEXT)
            base_layout(fig_units, "Units Sold by Reference")
            st.plotly_chart(fig_units, use_container_width=True)

        with col_r:
            fig_rev_prod = px.bar(
                perf.sort_values("total_revenue", ascending=True),
                x           = "total_revenue",
                y           = "name",
                orientation = "h",
                text        = perf.sort_values("total_revenue", ascending=True)["total_revenue"].apply(fmt_chf),
            )
            fig_rev_prod.update_traces(marker_color=LIGHT, textfont_color=TEXT)
            base_layout(fig_rev_prod, "Total Revenue by Reference")
            st.plotly_chart(fig_rev_prod, use_container_width=True)

        # ── Product Table ──────────────────────────────────────
        st.markdown("#### Reference Performance Table")
        display = perf[["name", "collection", "units_sold", "total_revenue", "avg_revenue_per_order"]].copy()
        display.columns = ["Reference", "Collection", "Units Sold", "Total Revenue (CHF)", "Avg. Order Value (CHF)"]
        display["Total Revenue (CHF)"]     = display["Total Revenue (CHF)"].apply(lambda x: f"{x:,.0f}")
        display["Avg. Order Value (CHF)"]  = display["Avg. Order Value (CHF)"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(display, use_container_width=True, hide_index=True)

        # ── Recommendations ────────────────────────────────────
        st.markdown("#### Product Recommendation Map")
        if not data["ml_recommendations"].empty and not data["dim_products"].empty:
            recs    = data["ml_recommendations"].copy()
            prods   = data["dim_products"][["product_id", "name"]].copy()
            recs    = recs.merge(prods.rename(columns={"product_id":"product_id",           "name":"from_product"}), on="product_id")
            recs    = recs.merge(prods.rename(columns={"product_id":"recommended_product_id","name":"to_product"}),   on="recommended_product_id")
            recs["similarity_score"] = recs["similarity_score"].round(3)
            display_recs = recs[["from_product", "to_product", "rank", "similarity_score"]]
            display_recs.columns = ["Reference", "Recommended", "Rank", "Similarity Score"]
            st.dataframe(display_recs, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
# TAB 3 — CUSTOMERS
# ══════════════════════════════════════════════════════════════
with tab_customers:

    if data["mart_rfm"].empty:
        st.warning("No customer data available.")
    else:
        rfm = data["mart_rfm"].copy()

        # ── KPI Row ────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Customers",   f"{len(rfm):,}")
        c2.metric("Avg. Recency",      f"{rfm['recency'].mean():.0f} days")
        c3.metric("Avg. Frequency",    f"{rfm['frequency'].mean():.1f} orders")
        c4.metric("Avg. Lifetime Spend", fmt_chf(rfm["monetary"].mean()))

        st.markdown("---")

        col_l, col_r = st.columns(2)

        with col_l:
            # RFM Segment distribution
            if not data["ml_segments"].empty:
                seg_counts = (
                    data["ml_segments"]
                    .groupby("segment_label")["customer_id"]
                    .count()
                    .reset_index()
                )
                seg_counts.columns = ["Segment", "Customers"]
                fig_seg = px.pie(
                    seg_counts,
                    names  = "Segment",
                    values = "Customers",
                    hole   = 0.55,
                )
                fig_seg.update_traces(
                    textfont_color = TEXT,
                    marker         = dict(
                        colors = [GOLD, LIGHT, "#8B6914", "#C9A84C"],
                        line   = dict(color=BG, width=2)
                    )
                )
                base_layout(fig_seg, "Customer Segments")
                st.plotly_chart(fig_seg, use_container_width=True)

        with col_r:
            # RFM scatter — recency vs monetary
            fig_rfm = px.scatter(
                rfm,
                x     = "recency",
                y     = "monetary",
                size  = "frequency",
                color = "rfm_score",
                color_continuous_scale = ["#3d2a0a", GOLD, LIGHT],
                labels = {"recency": "Recency (days)", "monetary": "Total Spend (CHF)", "rfm_score": "RFM Score"},
            )
            base_layout(fig_rfm, "RFM Distribution — Recency vs. Spend")
            fig_rfm.update_layout(coloraxis_colorbar=dict(tickfont=dict(color=MUTED)))
            st.plotly_chart(fig_rfm, use_container_width=True)

        # ── Segment Summary Table ──────────────────────────────
        if not data["ml_segments"].empty:
            st.markdown("#### Segment Summary")
            segs = data["ml_segments"].copy()
            seg_summary = segs.groupby("segment_label").agg(
                customers   = ("customer_id", "count"),
                avg_recency = ("recency",     "mean"),
                avg_orders  = ("frequency",   "mean"),
                avg_spend   = ("monetary",    "mean"),
            ).round(1).reset_index()
            seg_summary.columns = ["Segment", "Customers", "Avg. Recency (days)", "Avg. Orders", "Avg. Spend (CHF)"]
            seg_summary["Avg. Spend (CHF)"] = seg_summary["Avg. Spend (CHF)"].apply(lambda x: f"{x:,.0f}")
            st.dataframe(seg_summary, use_container_width=True, hide_index=True)

        # ── New Customers Over Time ────────────────────────────
        if not data["dim_customers"].empty:
            cust_df = data["dim_customers"].copy()
            cust_df["first_seen_at"] = pd.to_datetime(cust_df["first_seen_at"])
            cust_df["month"] = cust_df["first_seen_at"].dt.to_period("M").astype(str)
            new_per_month = cust_df.groupby("month")["customer_id"].count().reset_index()
            new_per_month.columns = ["Month", "New Customers"]

            fig_new = go.Figure(go.Bar(
                x             = new_per_month["Month"],
                y             = new_per_month["New Customers"],
                marker_color  = GOLD,
            ))
            base_layout(fig_new, "New Customers per Month")
            st.plotly_chart(fig_new, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 4 — FUNNEL
# ══════════════════════════════════════════════════════════════
with tab_funnel:

    if data["mart_funnel"].empty:
        st.warning("No funnel data available.")
    else:
        funnel = data["mart_funnel"].copy()
        funnel = funnel.sort_values("order")

        # ── Funnel Chart ───────────────────────────────────────
        fig_funnel = go.Figure(go.Funnel(
            y                = funnel["event_type"].str.replace("_", " ").str.title(),
            x                = funnel["count"],
            textposition     = "inside",
            textinfo         = "value+percent initial",
            marker           = dict(
                color      = [GOLD, LIGHT, "#C9A84C", "#8B6914", "#6B4F1A"],
                line       = dict(width=2, color=BG),
            ),
            connector        = dict(line=dict(color="#2a2018", width=1)),
        ))
        base_layout(fig_funnel, "Customer Purchase Funnel")
        fig_funnel.update_layout(margin=dict(t=60, b=40, l=200, r=40))
        st.plotly_chart(fig_funnel, use_container_width=True)

        # ── Conversion Rates ───────────────────────────────────
        st.markdown("#### Stage Conversion Rates")
        funnel["conversion_from_top"] = (funnel["count"] / funnel["count"].iloc[0] * 100).round(1)
        funnel["step_conversion"]     = (funnel["count"] / funnel["count"].shift(1) * 100).round(1)

        display_funnel = funnel[["event_type", "count", "conversion_from_top", "step_conversion"]].copy()
        display_funnel.columns = ["Stage", "Events", "Conversion from Top (%)", "Step Conversion (%)"]
        display_funnel["Stage"] = display_funnel["Stage"].str.replace("_", " ").str.title()
        st.dataframe(display_funnel, use_container_width=True, hide_index=True)

        # ── Events Over Time ───────────────────────────────────
        if not data["fact_events"].empty:
            events_df = data["fact_events"].copy()
            events_df["created_at"] = pd.to_datetime(events_df["created_at"])
            events_df = events_df[events_df["created_at"].dt.year.isin(selected_years)]
            events_df["month"] = events_df["created_at"].dt.to_period("M").astype(str)

            events_monthly = (
                events_df.groupby(["month", "event_type"])["id"]
                .count()
                .reset_index()
            )
            events_monthly.columns = ["Month", "Event Type", "Count"]

            fig_ev = px.line(
                events_monthly,
                x     = "Month",
                y     = "Count",
                color = "Event Type",
            )
            base_layout(fig_ev, "Events Over Time by Type")
            st.plotly_chart(fig_ev, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 5 — ML INSIGHTS
# ══════════════════════════════════════════════════════════════
with tab_ml:

    st.markdown("#### Machine Learning Model Outputs")
    st.markdown(
        "<span style='font-size:0.75rem;letter-spacing:0.1em;color:#9a8a6a'>"
        "Trained on synthetic transaction data. Models: KMeans Segmentation · "
        "Random Forest Churn · Gradient Boosting LTV · Cosine Similarity Recommendations"
        "</span>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    ml_col_l, ml_col_r = st.columns(2)

    # ── Churn Risk ─────────────────────────────────────────────
    with ml_col_l:
        if not data["ml_churn"].empty:
            churn = data["ml_churn"].copy()
            fig_churn = px.histogram(
                churn,
                x      = "churn_probability",
                nbins  = 20,
                labels = {"churn_probability": "Churn Probability", "count": "Customers"},
            )
            fig_churn.update_traces(marker_color=GOLD, marker_line_color=BG, marker_line_width=1)
            base_layout(fig_churn, "Churn Probability Distribution")
            st.plotly_chart(fig_churn, use_container_width=True)

            high_risk = churn[churn["churn_probability"] > 0.7]
            st.metric("High Risk Customers (>70%)", f"{len(high_risk):,}")

    # ── LTV Distribution ────────────────────────────────────────
    with ml_col_r:
        if not data["ml_ltv"].empty:
            ltv = data["ml_ltv"].copy()
            fig_ltv = px.scatter(
                ltv,
                x      = "ltv",
                y      = "predicted_ltv",
                labels = {"ltv": "Actual LTV (CHF)", "predicted_ltv": "Predicted LTV (CHF)"},
                opacity= 0.6,
            )
            # Perfect prediction line
            max_val = max(ltv["ltv"].max(), ltv["predicted_ltv"].max())
            fig_ltv.add_trace(go.Scatter(
                x    = [0, max_val],
                y    = [0, max_val],
                mode = "lines",
                name = "Perfect Prediction",
                line = dict(color=MUTED, dash="dash", width=1),
            ))
            fig_ltv.update_traces(marker_color=GOLD, selector=dict(mode="markers"))
            base_layout(fig_ltv, "LTV — Actual vs. Predicted")
            st.plotly_chart(fig_ltv, use_container_width=True)

    # ── Segment vs Churn vs LTV ────────────────────────────────
    if not data["ml_segments"].empty and not data["ml_churn"].empty and not data["ml_ltv"].empty:
        st.markdown("#### Segment Intelligence")
        merged = (
            data["ml_segments"][["customer_id", "segment_label", "recency", "frequency", "monetary"]]
            .merge(data["ml_churn"][["customer_id", "churn_probability"]], on="customer_id")
            .merge(data["ml_ltv"][["customer_id",   "predicted_ltv"]],    on="customer_id")
        )

        summary = merged.groupby("segment_label").agg(
            customers        = ("customer_id",       "count"),
            avg_churn_risk   = ("churn_probability", "mean"),
            avg_predicted_ltv= ("predicted_ltv",     "mean"),
            avg_spend        = ("monetary",           "mean"),
        ).round(1).reset_index()

        summary.columns = [
            "Segment", "Customers",
            "Avg. Churn Risk", "Avg. Predicted LTV (CHF)", "Avg. Historical Spend (CHF)"
        ]
        summary["Avg. Churn Risk"]              = summary["Avg. Churn Risk"].apply(lambda x: f"{x:.1%}")
        summary["Avg. Predicted LTV (CHF)"]     = summary["Avg. Predicted LTV (CHF)"].apply(lambda x: f"{x:,.0f}")
        summary["Avg. Historical Spend (CHF)"]  = summary["Avg. Historical Spend (CHF)"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(summary, use_container_width=True, hide_index=True)

        # ── Bubble Chart: Segment LTV vs Churn ────────────────
        fig_bubble = px.scatter(
            merged,
            x     = "predicted_ltv",
            y     = "churn_probability",
            color = "segment_label",
            size  = "monetary",
            labels = {
                "predicted_ltv"     : "Predicted LTV (CHF)",
                "churn_probability" : "Churn Probability",
                "segment_label"     : "Segment",
                "monetary"          : "Historical Spend",
            },
            opacity = 0.7,
        )
        base_layout(fig_bubble, "Customer Risk vs. Value — by Segment")
        st.plotly_chart(fig_bubble, use_container_width=True)