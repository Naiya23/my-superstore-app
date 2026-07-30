import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Global Superstore Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Color Theme
# -----------------------------
COLOR_MAIN = "#0072B2"
COLOR_ACCENT = "#D55E00"
COLOR_GRAY = "#BDBDBD"

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("Global_Superstore2.csv", encoding="latin1")

df = load_data()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Dashboard Filters")

regions = st.sidebar.multiselect(
    "Select Region",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

filtered_df = df[df["Region"].isin(regions)]

# -----------------------------
# Dashboard Title
# -----------------------------
st.title("🌍 Global Superstore Dashboard")
st.markdown("### Sales and Profit Analysis by Region")

# -----------------------------
# KPI Metrics
# -----------------------------
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = filtered_df["Order ID"].nunique()

col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Profit", f"${total_profit:,.0f}")
col3.metric("Orders", f"{total_orders:,}")

st.divider()

# -----------------------------
# Sales & Profit by Region
# -----------------------------
summary = (
    filtered_df.groupby("Region")[["Sales", "Profit"]]
    .sum()
    .reset_index()
)

fig = px.bar(
    summary,
    x="Region",
    y=["Sales", "Profit"],
    barmode="group",
    color_discrete_sequence=[COLOR_MAIN, COLOR_ACCENT],
    title="Sales and Profit by Region",
    template="simple_white"
)

fig.update_layout(
    title_x=0.5,
    legend_title="Metric",
    height=500
)

highest_region = summary.loc[summary["Sales"].idxmax()]

fig.add_annotation(
    x=highest_region["Region"],
    y=highest_region["Sales"],
    text="Highest Sales",
    showarrow=True,
    arrowhead=2
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Summary Table
# -----------------------------
st.subheader("Regional Summary")

st.dataframe(
    summary.style.format({
        "Sales": "${:,.0f}",
        "Profit": "${:,.0f}"
    }),
    use_container_width=True
)

# -----------------------------
# Raw Data
# -----------------------------
with st.expander("View Raw Data"):
    st.dataframe(filtered_df, use_container_width=True)
