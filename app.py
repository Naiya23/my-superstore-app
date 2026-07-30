#Which regions generate the highest sales and profit?
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
    #How has monthly sales changed over time across different markets?
import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Global Superstore Dashboard",
    page_icon="📈",
    layout="wide"
)

# -----------------------------------
# Load Data
# -----------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Global_Superstore2.csv", encoding="latin1")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
    return df

df = load_data()

# -----------------------------------
# Dashboard Title
# -----------------------------------
st.title("📈 Global Superstore Dashboard")
st.subheader("Monthly Sales Trends Across Different Markets")

# -----------------------------------
# Sidebar Filter
# -----------------------------------
markets = sorted(df["Market"].unique())

selected_markets = st.sidebar.multiselect(
    "Select Market",
    markets,
    default=markets
)

filtered_df = df[df["Market"].isin(selected_markets)]

# -----------------------------------
# Monthly Sales Calculation
# -----------------------------------
monthly_sales = (
    filtered_df.groupby(["Month", "Market"])["Sales"]
    .sum()
    .reset_index()
)

monthly_sales["Month"] = pd.to_datetime(monthly_sales["Month"])

# -----------------------------------
# Plotly Line Chart
# -----------------------------------
fig = px.line(
    monthly_sales,
    x="Month",
    y="Sales",
    color="Market",
    markers=True,
    color_discrete_sequence=px.colors.qualitative.Safe,
    title="Monthly Sales Trends Across Different Markets",
    labels={
        "Month": "Month",
        "Sales": "Total Sales ($)",
        "Market": "Market"
    },
    template="simple_white"
)

fig.update_layout(
    title={
        "text": "Monthly Sales Trends Across Different Markets",
        "x": 0.5,
        "xanchor": "center"
    },
    font=dict(
        family="Arial",
        size=15
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
    legend_title="Market",
    hovermode="x unified",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="lightgray"),
    height=600
)

# -----------------------------------
# Display Chart
# -----------------------------------
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# KPI Metrics
# -----------------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", f"${filtered_df['Sales'].sum():,.0f}")
col2.metric("Total Profit", f"${filtered_df['Profit'].sum():,.0f}")
col3.metric("Total Orders", filtered_df["Order ID"].nunique())

# -----------------------------------
# Monthly Sales Table
# -----------------------------------
st.subheader("Monthly Sales Summary")

st.dataframe(
    monthly_sales,
    use_container_width=True
)

# -----------------------------------
# Raw Data
# -----------------------------------
with st.expander("View Raw Data"):
    st.dataframe(filtered_df, use_container_width=True)
