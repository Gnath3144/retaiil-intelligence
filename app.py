"""
================================================================================
Retail Intelligence Platform - Streamlit Dashboard
================================================================================
A professional, executive-ready dashboard powered by Snowflake Gold-layer analytics.
Demonstrates end-to-end Medallion data engineering insights with interactive visualisations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from snowflake_db import (
    fetch_sales_by_category,
    fetch_top_products,
    get_mock_data,
    get_snowflake_config,
)

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Retail Intelligence Platform",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a sleek, modern, and polished executive dashboard look
st.markdown(
    """
    <style>
        /* Global font styling */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Metric card styling */
        .metric-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        .metric-label {
            font-size: 0.85rem;
            font-weight: 500;
            color: #888888;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1f77b4;
            margin-bottom: 2px;
        }
        .metric-sub {
            font-size: 0.8rem;
            color: #666666;
        }

        /* Insight callout box */
        .insight-card {
            background: linear-gradient(135deg, #f0f7ff, #e6f0fa);
            border-left: 5px solid #0066cc;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 12px;
            color: #1a365d;
        }
        @media (prefers-color-scheme: dark) {
            .insight-card {
                background: linear-gradient(135deg, #132338, #1a2e47);
                color: #e2e8f0;
                border-left-color: #3182ce;
            }
        }

        /* Architecture step card */
        .arch-node {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            font-weight: 600;
            color: #334155;
            margin: 4px 0;
        }
        @media (prefers-color-scheme: dark) {
            .arch-node {
                background-color: #1e293b;
                border-color: #334155;
                color: #f1f5f9;
            }
        }
        .arch-arrow {
            text-align: center;
            font-size: 1.2rem;
            color: #0066cc;
            font-weight: bold;
        }

        /* Product rank badge */
        .rank-badge {
            background-color: #0066cc;
            color: white;
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 2. Data Loading with Caching & Graceful Error Handling
# -----------------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner="Querying Snowflake Gold Layer...")
def load_data_from_snowflake():
    """
    Load Gold layer tables from Snowflake with caching (10 min TTL).
    Returns (sales_by_category_df, top_products_df, is_live_connection, error_msg).
    """
    try:
        # Check if environment variables are configured
        _ = get_snowflake_config()
        cat_df = fetch_sales_by_category()
        prod_df = fetch_top_products()
        return cat_df, prod_df, True, None
    except Exception as e:
        # Fall back to sample demo data if Snowflake is not reachable or unconfigured
        cat_mock, prod_mock = get_mock_data()
        return cat_mock, prod_mock, False, str(e)


# Load dataset
category_df_raw, top_products_df_raw, is_live, conn_error = load_data_from_snowflake()


# -----------------------------------------------------------------------------
# 3. Sidebar Controls & Connection Status
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shop.png", width=64)
    st.title("Filters & Settings")

    # Connection Status Indicator
    if is_live:
        st.success("🟢 Connected to Snowflake (Live)")
        with st.expander("Connection Details"):
            st.write("**Database:** `MEDICAPS_RETAIL`")
            st.write("**Schema:** `GOLD`")
            st.write("**Tables:** `SALES_BY_CATEGORY`, `TOP_PRODUCTS`")
    else:
        st.warning("🟡 Using Demo Sample Data")
        with st.expander("Connection Notice & Setup"):
            st.info(
                "Could not connect to live Snowflake instance. Showing built-in mock data."
            )
            if conn_error:
                st.caption(f"**Error Details:** {conn_error}")
            st.markdown(
                """
                **To connect to Snowflake:**
                1. Copy `.env.example` to `.env`
                2. Add your Snowflake credentials
                3. Click **Refresh Data** below
                """
            )

    st.markdown("---")

    # Category Filter
    all_categories = sorted(category_df_raw["CATEGORY"].dropna().unique().tolist())
    category_filter = st.selectbox(
        "Filter by Category",
        options=["All Categories"] + all_categories,
        index=0,
        help="Select a category to filter KPI metrics, charts, and product leaderboards.",
    )

    st.markdown("---")

    # Refresh Data Button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Retail Intelligence Platform v1.0")
    st.caption("Powered by Snowflake & Streamlit")


# -----------------------------------------------------------------------------
# 4. Header Section
# -----------------------------------------------------------------------------
st.title("🛍️ Retail Intelligence Platform")
st.markdown(
    "##### *Enterprise retail performance analysis powered by Snowflake's curated Gold Layer dataset.*"
)
st.caption(
    "This dashboard analyzes high-value retail transactions, category revenue shares, and top-performing merchandise across physical and digital storefronts."
)
st.write("")


# -----------------------------------------------------------------------------
# 5. Filter Data Based on User Selection
# -----------------------------------------------------------------------------
if category_filter != "All Categories":
    filtered_cat_df = category_df_raw[category_df_raw["CATEGORY"] == category_filter].copy()
    filtered_prod_df = top_products_df_raw[top_products_df_raw["CATEGORY"] == category_filter].copy()
else:
    filtered_cat_df = category_df_raw.copy()
    filtered_prod_df = top_products_df_raw.copy()


# Ensure sorting
filtered_cat_df = filtered_cat_df.sort_values(by="TOTAL_REVENUE", ascending=False)


# -----------------------------------------------------------------------------
# 6. Executive KPI Cards
# -----------------------------------------------------------------------------
st.subheader("📊 Key Performance Indicators (KPIs)")

total_revenue = filtered_cat_df["TOTAL_REVENUE"].sum()
total_units = filtered_cat_df["TOTAL_UNITS"].sum()
total_txns = filtered_cat_df["TOTAL_TRANSACTIONS"].sum()
# Weighted Average Transaction Value
avg_txn_value = (
    total_revenue / total_txns if total_txns > 0 else 0.0
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">${total_revenue:,.2f}</div>
            <div class="metric-sub">Across selected categories</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Units Sold</div>
            <div class="metric-value">{int(total_units):,}</div>
            <div class="metric-sub">Items dispatched</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Transactions</div>
            <div class="metric-value">{int(total_txns):,}</div>
            <div class="metric-sub">Customer checkout orders</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Avg Transaction Value</div>
            <div class="metric-value">${avg_txn_value:,.2f}</div>
            <div class="metric-sub">Revenue per order</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.write("")


# -----------------------------------------------------------------------------
# 7. Category Analysis (Interactive Plotly Charts)
# -----------------------------------------------------------------------------
st.subheader("📈 Category Performance Analysis")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    # Bar chart of Revenue by Category (Sorted Descending)
    chart_df_rev = category_df_raw.sort_values(by="TOTAL_REVENUE", ascending=True)
    fig_rev = px.bar(
        chart_df_rev,
        x="TOTAL_REVENUE",
        y="CATEGORY",
        orientation="h",
        title="<b>Total Revenue by Category</b>",
        text_auto="$,.0f",
        labels={"TOTAL_REVENUE": "Total Revenue (USD)", "CATEGORY": "Category"},
        color="TOTAL_REVENUE",
        color_continuous_scale="Blues",
    )
    fig_rev.update_layout(
        showlegend=False,
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Revenue ($)",
        yaxis_title="",
    )
    fig_rev.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>",
    )
    st.plotly_chart(fig_rev, use_container_width=True)

with col_chart2:
    # Bar chart of Units Sold by Category (Sorted by Revenue Descending for consistency)
    chart_df_units = category_df_raw.sort_values(by="TOTAL_REVENUE", ascending=True)
    fig_units = px.bar(
        chart_df_units,
        x="TOTAL_UNITS",
        y="CATEGORY",
        orientation="h",
        title="<b>Units Sold by Category</b>",
        text_auto=",",
        labels={"TOTAL_UNITS": "Units Sold", "CATEGORY": "Category"},
        color="TOTAL_UNITS",
        color_continuous_scale="Teal",
    )
    fig_units.update_layout(
        showlegend=False,
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Units Sold",
        yaxis_title="",
    )
    fig_units.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Units Sold: %{x:,}<extra></extra>",
    )
    st.plotly_chart(fig_units, use_container_width=True)

st.write("")


# -----------------------------------------------------------------------------
# 8. Product Analysis (Configurable Top-N Product Leaderboard)
# -----------------------------------------------------------------------------
st.subheader("🏆 Product Leaderboard")

prod_col1, prod_col2 = st.columns([1, 2])

with prod_col1:
    st.markdown("##### Configuration")
    
    # Category dropdown for product drill-down
    prod_cat_options = ["All Categories"] + all_categories
    default_cat_idx = (
        0 if category_filter == "All Categories" 
        else prod_cat_options.index(category_filter) if category_filter in prod_cat_options else 0
    )
    selected_prod_cat = st.selectbox(
        "Select Category Drill-down",
        options=prod_cat_options,
        index=default_cat_idx,
        key="prod_cat_selector",
        help="Select a category to view top performing products or view across all categories."
    )

    # Top-N selector (Top 3, Top 5, Top 10)
    top_n_limit = st.radio(
        "Display Limit",
        options=[3, 5, 10],
        index=1,  # Default to Top 5
        format_func=lambda x: f"Top {x} Products",
        horizontal=True,
        help="Configure how many top products to display."
    )

    # Filter products
    if selected_prod_cat == "All Categories":
        cat_top_prods = top_products_df_raw.sort_values(by=["REVENUE", "PRODUCT_RANK"], ascending=[False, True]).head(top_n_limit)
        display_scope = "across all categories"
    else:
        cat_top_prods = top_products_df_raw[
            top_products_df_raw["CATEGORY"] == selected_prod_cat
        ].sort_values(by=["PRODUCT_RANK", "REVENUE"], ascending=[True, False]).head(top_n_limit)
        display_scope = f"in **{selected_prod_cat}**"

    st.markdown(
        f"""
        Displaying the **Top {len(cat_top_prods)} products** by revenue {display_scope}.
        Rankings are computed dynamically from Snowflake Gold layer models.
        """
    )

with prod_col2:
    if not cat_top_prods.empty:
        # Display top products in clean cards
        for idx, row in cat_top_prods.reset_index(drop=True).iterrows():
            rank = idx + 1
            p_name = row["PRODUCT_NAME"]
            p_rev = float(row["REVENUE"])
            p_cat = row.get("CATEGORY", selected_prod_cat)
            
            # Badge icon mapping
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"
            elif rank == 4:
                medal = "4️⃣"
            elif rank == 5:
                medal = "5️⃣"
            else:
                medal = "🏅"

            st.markdown(
                f"""
                <div style="background: rgba(128,128,128,0.06); border-radius: 10px; padding: 12px 18px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; border: 1px solid rgba(128,128,128,0.15);">
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <span style="font-size: 1.4rem;">{medal}</span>
                        <div>
                            <span class="rank-badge">Rank #{rank}</span>
                            <div style="font-weight: 600; font-size: 1.0rem; margin-top: 3px;">{p_name}</div>
                            <div style="font-size: 0.78rem; color: #777;">Category: {p_cat}</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2rem; font-weight: 700; color: #28a745;">${p_rev:,.2f}</div>
                        <div style="font-size: 0.72rem; color: #888;">Total Sales</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No product ranking records found for this category.")

st.write("")
st.write("")


# -----------------------------------------------------------------------------
# 9. Business Insights
# -----------------------------------------------------------------------------
st.subheader("💡 Automated Business Insights")

# Compute dynamic analytical insights
if not category_df_raw.empty:
    highest_rev_cat_row = category_df_raw.loc[category_df_raw["TOTAL_REVENUE"].idxmax()]
    highest_vol_cat_row = category_df_raw.loc[category_df_raw["TOTAL_UNITS"].idxmax()]
    overall_avg_txn = (
        category_df_raw["TOTAL_REVENUE"].sum() / category_df_raw["TOTAL_TRANSACTIONS"].sum()
        if category_df_raw["TOTAL_TRANSACTIONS"].sum() > 0
        else 0
    )
else:
    highest_rev_cat_row = None
    highest_vol_cat_row = None
    overall_avg_txn = 0

if not top_products_df_raw.empty:
    highest_rev_prod_row = top_products_df_raw.loc[top_products_df_raw["REVENUE"].idxmax()]
else:
    highest_rev_prod_row = None

ins_col1, ins_col2 = st.columns(2)

with ins_col1:
    if highest_rev_cat_row is not None:
        st.markdown(
            f"""
            <div class="insight-card">
                <strong>👑 Highest Revenue Category:</strong><br>
                <span style="font-size: 1.15rem; font-weight: 600;">{highest_rev_cat_row['CATEGORY']}</span> generates 
                <strong>${highest_rev_cat_row['TOTAL_REVENUE']:,.2f}</strong>, leading the store portfolio.
            </div>
            """,
            unsafe_allow_html=True,
        )

    if highest_vol_cat_row is not None:
        st.markdown(
            f"""
            <div class="insight-card">
                <strong>📦 Highest Volume Category:</strong><br>
                <span style="font-size: 1.15rem; font-weight: 600;">{highest_vol_cat_row['CATEGORY']}</span> sold 
                <strong>{int(highest_vol_cat_row['TOTAL_UNITS']):,} units</strong>, capturing the largest volume share.
            </div>
            """,
            unsafe_allow_html=True,
        )

with ins_col2:
    if highest_rev_prod_row is not None:
        st.markdown(
            f"""
            <div class="insight-card">
                <strong>🌟 Top-Selling Product Overall:</strong><br>
                <span style="font-size: 1.15rem; font-weight: 600;">{highest_rev_prod_row['PRODUCT_NAME']}</span> 
                ({highest_rev_prod_row['CATEGORY']}) with <strong>${highest_rev_prod_row['REVENUE']:,.2f}</strong> in revenue.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="insight-card">
            <strong>💳 Overall Average Transaction Value (ATV):</strong><br>
            Average customer spend across all transactions is <strong>${overall_avg_txn:,.2f}</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.write("")


# -----------------------------------------------------------------------------
# 10. Medallion Data Architecture Section
# -----------------------------------------------------------------------------
st.subheader("🏗️ Architecture Overview")
st.markdown(
    """
    The **Retail Intelligence Platform** is built on a **Medallion Data Architecture** in Snowflake.
    Data is cleaned, transformed, and aggregated across distinct storage layers before being rendered in Streamlit:
    """
)

arch_col1, arch_col2, arch_col3, arch_col4, arch_col5 = st.columns(5)

with arch_col1:
    st.markdown(
        """
        <div class="arch-node">
            <div>📥 <strong>Source</strong></div>
            <small style="color: #666;">Raw POS & E-Commerce Event Logs</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

with arch_col2:
    st.markdown(
        """
        <div class="arch-node">
            <div>🥉 <strong>Bronze</strong></div>
            <small style="color: #666;">Raw ingestion tables (Append-only staging)</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

with arch_col3:
    st.markdown(
        """
        <div class="arch-node">
            <div>🥈 <strong>Silver</strong></div>
            <small style="color: #666;">Cleaned, typed, deduplicated sales records</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

with arch_col4:
    st.markdown(
        """
        <div class="arch-node">
            <div>🥇 <strong>Gold</strong></div>
            <small style="color: #666;">Aggregated business marts (Sales & Top Products)</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

with arch_col5:
    st.markdown(
        """
        <div class="arch-node">
            <div>⚡ <strong>Streamlit App</strong></div>
            <small style="color: #666;">Interactive analytical executive UI</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    ```text
    [Source Systems] ──> [Bronze Layer] ──> [Silver Layer] ──> [Gold Layer] ──> [Streamlit Dashboard]
    (Raw Ingestion)       (Staging Logs)      (Clean Sales)      (Aggregates)      (Business Intelligence)
    ```
    """
)

st.write("")
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 0.85rem;'>Retail Intelligence Platform • Powered by Streamlit & Snowflake • Secure Environment Variables</div>",
    unsafe_allow_html=True,
)
