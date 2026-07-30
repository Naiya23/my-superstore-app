"""Interactive Global Superstore business dashboard.

This application recreates the twelve analyses from the accompanying notebook
using the same fields, aggregations, rankings, and calculations.
"""

from __future__ import annotations

from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_FILE = "Global_Superstore2.csv"
PRIMARY_COLOR = "#0072B2"
ACCENT_COLOR = "#D55E00"
SAFE_COLORS = px.colors.qualitative.Safe
PLOTLY_CONFIG = {
    "displaylogo": False,
    "toImageButtonOptions": {"format": "png", "filename": "global_superstore_chart", "scale": 2},
}


@st.cache_data(show_spinner="Loading Global Superstore data...")
def load_data() -> pd.DataFrame:
    """Load and prepare the assignment dataset once per session."""
    data = pd.read_csv(DATA_FILE, encoding="latin1")
    data["Order Date"] = pd.to_datetime(data["Order Date"], dayfirst=True, errors="coerce")
    data["Ship Date"] = pd.to_datetime(data["Ship Date"], dayfirst=True, errors="coerce")
    data["Year"] = data["Order Date"].dt.year.astype("Int64")
    # This is the delivery-performance calculation used in the notebook.
    data["Delivery Days"] = (data["Ship Date"] - data["Order Date"]).dt.days
    return data


def money(value: float) -> str:
    """Format a value as compact currency for KPIs."""
    return f"${value:,.0f}"


def style_figure(fig, height: int = 560):
    """Apply a consistent professional Plotly appearance."""
    height = min(height, 440)
    fig.update_layout(
        template="simple_white",
        title_x=0.5,
        font={"family": "Arial, sans-serif", "size": 14, "color": "#1f2937"},
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=height,
        margin={"l": 35, "r": 30, "t": 75, "b": 40},
        hoverlabel={"bgcolor": "white", "font_size": 13},
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#e5e7eb", zeroline=True, zerolinecolor="#d1d5db")
    return fig


def show_chart(fig) -> None:
    """Render a responsive chart with Plotly's interaction toolbar."""
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)


def show_insights(items: list[str]) -> None:
    """Display concise findings based solely on the current chart aggregation."""
    st.markdown("**Business insight**")
    for item in items:
        st.markdown(f"- {item}")


def show_empty() -> bool:
    """Guard an analysis section when filter selections yield no records."""
    if st.session_state.get("filtered_rows", 0) == 0:
        st.info("No records match the selected filters. Adjust the sidebar filters to view this analysis.")
        return True
    return False


def create_sidebar(data: pd.DataFrame) -> pd.DataFrame:
    """Create shared, applicable filters and return their filtered dataset."""
    st.sidebar.header("Dashboard filters")
    st.sidebar.caption("Selections apply to every KPI and business question.")

    filter_columns = [
        ("Market", "Market"),
        ("Region", "Region"),
        ("Country", "Country"),
        ("Category", "Category"),
        ("Sub Category", "Sub-Category"),
        ("Segment", "Segment"),
        ("Ship Mode", "Ship Mode"),
    ]

    selections: dict[str, list] = {}
    for label, column in filter_columns:
        options = sorted(data[column].dropna().unique().tolist())
        selections[column] = st.sidebar.multiselect(label, options=options, default=options)

    years = sorted(data["Year"].dropna().astype(int).unique().tolist())
    selections["Year"] = st.sidebar.multiselect("Year", options=years, default=years)

    filtered = data.copy()
    for column, selected in selections.items():
        filtered = filtered[filtered[column].isin(selected)]

    st.sidebar.divider()
    st.sidebar.caption(f"**{len(filtered):,}** of **{len(data):,}** records selected")
    return filtered


def display_kpis(data: pd.DataFrame) -> None:
    """Show the assignment's headline sales, profit, order, and customer metrics."""
    columns = st.columns(4)
    metrics = [
        ("sales", "Total Sales", money(data["Sales"].sum())),
        ("profit", "Total Profit", money(data["Profit"].sum())),
        ("orders", "Total Orders", f"{data['Order ID'].nunique():,}"),
        ("customers", "Total Customers", f"{data['Customer ID'].nunique():,}"),
    ]
    for column, (card_class, label, value) in zip(columns, metrics):
        column.markdown(
            f'<div class="kpi-card {card_class}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',
            unsafe_allow_html=True,
        )


def section_header(number: int, question: str) -> None:
    st.markdown(f"### Question {number}")
    st.markdown(f"*{question}*")


def question1(data: pd.DataFrame) -> None:
    question = "Which regions generate the highest sales and profit?"
    with st.container():
        section_header(1, question)
        if data.empty or show_empty():
            return
        summary = data.groupby("Region")[["Sales", "Profit"]].sum().reset_index()
        highest = summary.loc[summary["Sales"].idxmax()]
        fig = px.bar(summary, x="Region", y=["Sales", "Profit"], barmode="group",
                     color_discrete_sequence=[PRIMARY_COLOR, ACCENT_COLOR],
                     title="Regions differ substantially in both sales and profitability",
                     labels={"value": "Amount ($)", "variable": "Measure"})
        fig.add_annotation(x=highest["Region"], y=highest["Sales"], text="Highest Sales", showarrow=True, arrowhead=2)
        style_figure(fig)
        show_chart(fig)
        best_profit = summary.loc[summary["Profit"].idxmax()]
        show_insights([f"{highest['Region']} generates the highest total sales ({money(highest['Sales'])}).",
                       f"{best_profit['Region']} generates the highest total profit ({money(best_profit['Profit'])})."])


def question2(data: pd.DataFrame) -> None:
    question = "How has monthly sales changed over time across different markets?"
    with st.container():
        section_header(2, question)
        if data.empty or show_empty():
            return
        monthly = data.assign(Month=data["Order Date"].dt.to_period("M").dt.to_timestamp()).groupby(["Month", "Market"])["Sales"].sum().reset_index()
        highest = monthly.loc[monthly["Sales"].idxmax()]
        fig = px.line(monthly, x="Month", y="Sales", color="Market", markers=True,
                      color_discrete_sequence=SAFE_COLORS, title="Monthly Sales Trends Across Different Markets",
                      labels={"Sales": "Total Sales ($)", "Month": "Month"})
        fig.update_layout(hovermode="x unified", legend_title="Market")
        fig.add_annotation(x=highest["Month"], y=highest["Sales"], text="Highest Monthly Sales", showarrow=True, arrowhead=2, bgcolor="#fef3c7")
        style_figure(fig, 620)
        show_chart(fig)
        show_insights([f"The peak monthly market result is {highest['Market']} in {highest['Month']:%b %Y} ({money(highest['Sales'])}).",
                       "The line chart preserves the notebook's month-by-market sales aggregation for comparing trends over time."])


def question3(data: pd.DataFrame) -> None:
    question = "Which product categories are most profitable?"
    with st.container():
        section_header(3, question)
        if data.empty or show_empty(): return
        summary = data.groupby("Category")["Profit"].sum().reset_index().sort_values("Profit", ascending=False)
        highest = summary.iloc[0]
        fig = px.bar(summary, x="Category", y="Profit", color="Category", text_auto=".2s",
                     color_discrete_sequence=SAFE_COLORS, title="Technology Generates the Highest Profit Among Product Categories",
                     labels={"Profit": "Total Profit ($)", "Category": "Product Category"})
        fig.update_layout(showlegend=False)
        fig.add_annotation(x=highest["Category"], y=highest["Profit"], text="Highest Profit", showarrow=True, arrowhead=2, bgcolor="#fef3c7")
        style_figure(fig)
        show_chart(fig)
        show_insights([f"{highest['Category']} is the most profitable category at {money(highest['Profit'])}.",
                       f"The category ranking is calculated from total profit, matching the notebook."])


def question4(data: pd.DataFrame) -> None:
    question = "Does offering higher discounts actually increase profit?"
    with st.container():
        section_header(4, question)
        if data.empty or show_empty(): return
        highest = data.loc[data["Profit"].idxmax()]
        fig = px.scatter(data, x="Discount", y="Profit", color="Category", opacity=0.65,
                         color_discrete_sequence=SAFE_COLORS, title="Higher Discounts Do Not Necessarily Increase Profit",
                         labels={"Discount": "Discount (%)", "Profit": "Profit ($)", "Category": "Product Category"},
                         hover_data=["Sales", "Region", "Sub-Category"])
        fig.add_annotation(x=highest["Discount"], y=highest["Profit"], text="Highest Profit", showarrow=True, arrowhead=2, bgcolor="#fef3c7")
        style_figure(fig, 620)
        show_chart(fig)
        show_insights([f"The highest-profit order earns {money(highest['Profit'])} at a {highest['Discount']:.0%} discount.",
                       "The order-level scatter shows profit varies at each discount level rather than increasing uniformly with discount."])


def question5(data: pd.DataFrame) -> None:
    question = "Which sub-categories generate high sales but low profit?"
    with st.container():
        section_header(5, question)
        if data.empty or show_empty(): return
        summary = data.groupby("Sub-Category")[["Sales", "Profit"]].sum().reset_index().sort_values(["Sales", "Profit"], ascending=[False, True]).head(10)
        lowest = summary.loc[summary["Profit"].idxmin()]
        fig = px.bar(summary, x="Sales", y="Sub-Category", orientation="h", color="Profit", text="Profit",
                     color_continuous_scale="RdYlGn", title="Top Selling Sub-Categories with Low Profit",
                     labels={"Sales": "Total Sales ($)", "Profit": "Total Profit ($)"})
        fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside", hovertemplate="<b>%{y}</b><br>Sales: $%{x:,.0f}<br>Profit: $%{marker.color:,.0f}<extra></extra>")
        fig.update_yaxes(categoryorder="total ascending")
        fig.add_annotation(x=lowest["Sales"], y=lowest["Sub-Category"], text="High Sales, Lowest Profit", showarrow=True, arrowhead=2, bgcolor="#fef3c7")
        style_figure(fig, 640)
        show_chart(fig)
        show_insights([f"Among the top 10 sub-categories by sales, {lowest['Sub-Category']} has the lowest profit ({money(lowest['Profit'])}).",
                       "The selection retains the notebook's sort: sales descending, then profit ascending, followed by the top 10."])


def question6(data: pd.DataFrame) -> None:
    question = "Which customer segments are the most profitable across markets?"
    with st.container():
        section_header(6, question)
        if data.empty or show_empty(): return
        summary = data.groupby(["Market", "Segment"])["Profit"].sum().reset_index()
        market_profit = summary.groupby("Market")["Profit"].sum().reset_index()
        highest = market_profit.loc[market_profit["Profit"].idxmax()]
        best_segment = summary.loc[summary["Profit"].idxmax()]
        fig = px.bar(summary, x="Market", y="Profit", color="Segment", barmode="stack", text_auto=".2s",
                     color_discrete_sequence=SAFE_COLORS, title="Customer Segments Driving Profit Across Different Markets",
                     labels={"Profit": "Total Profit ($)", "Segment": "Customer Segment"})
        fig.update_layout(legend_title="Customer Segment")
        fig.add_annotation(x=highest["Market"], y=highest["Profit"], text="Highest Total Profit", showarrow=True, arrowhead=2, bgcolor="#fef3c7")
        style_figure(fig, 620)
        show_chart(fig)
        show_insights([f"{highest['Market']} has the highest total market profit ({money(highest['Profit'])}).",
                       f"The largest market-segment profit contribution is {best_segment['Segment']} in {best_segment['Market']} ({money(best_segment['Profit'])})."])


def question7(data: pd.DataFrame) -> None:
    question = "Which countries have high sales but poor profit margins?"
    with st.container():
        section_header(7, question)
        if data.empty or show_empty(): return
        country = data.groupby("Country")[["Sales", "Profit"]].sum().reset_index()
        country["Profit Margin (%)"] = country["Profit"] / country["Sales"] * 100
        country = country.sort_values("Sales", ascending=False)
        lowest = country.loc[country["Profit Margin (%)"].idxmin()]
        fig = px.scatter(country, x="Sales", y="Profit Margin (%)", size="Sales", color="Profit Margin (%)", hover_name="Country",
                         color_continuous_scale="RdYlGn", size_max=45, title="Countries with High Sales but Poor Profit Margins",
                         labels={"Sales": "Total Sales ($)", "Profit Margin (%)": "Profit Margin (%)"})
        fig.add_annotation(x=lowest["Sales"], y=lowest["Profit Margin (%)"], text=lowest["Country"], showarrow=True, arrowhead=2, bgcolor="#fef3c7")
        style_figure(fig, 620)
        show_chart(fig)
        show_insights([f"{lowest['Country']} has the lowest profit margin ({lowest['Profit Margin (%)']:.2f}%) in the current selection.",
                       "Profit margin is retained as total profit divided by total sales, multiplied by 100."])


def question8(data: pd.DataFrame) -> None:
    question = "How does shipping mode affect delivery performance and profit?"
    with st.container():
        section_header(8, question)
        if data.empty or show_empty(): return
        avg_profit = data.groupby("Ship Mode")["Profit"].mean().reset_index()
        best = avg_profit.loc[avg_profit["Profit"].idxmax()]
        fig = px.box(data, x="Ship Mode", y="Profit", color="Ship Mode", points="outliers", color_discrete_sequence=SAFE_COLORS,
                     title="Profit Distribution Across Different Shipping Modes", labels={"Profit": "Profit ($)", "Ship Mode": "Shipping Mode"})
        fig.update_layout(showlegend=False)
        fig.add_annotation(x=best["Ship Mode"], y=data["Profit"].max(), text="Highest Average Profit", showarrow=True, arrowhead=2, bgcolor="#fef3c7")
        style_figure(fig)
        show_chart(fig)
        show_insights([f"{best['Ship Mode']} has the highest average profit ({money(best['Profit'])}) among shipping modes.",
                       f"Delivery days are calculated as ship date minus order date; the notebook's visualization compares the resulting profit distributions by ship mode."])


def question9(data: pd.DataFrame) -> None:
    question = "What are the Top 15 most profitable products?"
    with st.container():
        section_header(9, question)
        if data.empty or show_empty(): return
        products = data.groupby("Product Name")["Profit"].sum().reset_index().sort_values("Profit", ascending=False).head(15)
        best = products.iloc[0]
        fig = px.bar(products, x="Profit", y="Product Name", orientation="h", color="Profit", text_auto=".2s",
                     color_continuous_scale="Blues", title="Top 15 Most Profitable Products",
                     labels={"Profit": "Total Profit ($)", "Product Name": "Product"})
        fig.update_layout(coloraxis_showscale=False)
        fig.update_yaxes(categoryorder="total ascending")
        fig.add_annotation(x=best["Profit"], y=best["Product Name"], text="Highest Profit", showarrow=True, arrowhead=2, bgcolor="#fef3c7")
        style_figure(fig, 700)
        show_chart(fig)
        show_insights([f"{best['Product Name']} is the most profitable product ({money(best['Profit'])}).",
                       "Products are ranked by summed profit and restricted to the top 15, exactly as in the notebook."])


def question10(data: pd.DataFrame) -> None:
    question = "How do sales and profit vary across months and categories?"
    with st.container():
        section_header(10, question)
        if data.empty or show_empty(): return
        month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        month_data = data.assign(Month=pd.Categorical(data["Order Date"].dt.month_name(), categories=month_order, ordered=True))
        sales_heatmap = month_data.pivot_table(values="Sales", index="Category", columns="Month", aggfunc="sum", observed=False).reindex(columns=month_order)
        profit_heatmap = month_data.pivot_table(values="Profit", index="Category", columns="Month", aggfunc="sum", observed=False).reindex(columns=month_order)
        left, right = st.columns(2)
        with left:
            fig_sales = px.imshow(sales_heatmap, text_auto=".0f", color_continuous_scale="Blues", title="Monthly Sales by Product Category", labels={"color": "Sales ($)"})
            style_figure(fig_sales, 480)
            show_chart(fig_sales)
        with right:
            fig_profit = px.imshow(profit_heatmap, text_auto=".0f", color_continuous_scale="Greens", title="Monthly Profit by Product Category", labels={"color": "Profit ($)"})
            style_figure(fig_profit, 480)
            show_chart(fig_profit)
        peak_sales = sales_heatmap.stack().idxmax()
        peak_profit = profit_heatmap.stack().idxmax()
        show_insights([f"The highest category-month sales value is {peak_sales[0]} in {peak_sales[1]} ({money(sales_heatmap.loc[peak_sales])}).",
                       f"The highest category-month profit value is {peak_profit[0]} in {peak_profit[1]} ({money(profit_heatmap.loc[peak_profit])})."])


def question11(data: pd.DataFrame) -> None:
    question = "Which cities consistently generate losses despite high sales?"
    with st.container():
        section_header(11, question)
        if data.empty or show_empty(): return
        cities = data.groupby("City")[["Sales", "Profit"]].sum().reset_index()
        losses = cities[cities["Profit"] < 0].sort_values("Sales", ascending=False)
        if losses.empty:
            st.info("No cities have negative total profit for the selected filters.")
            return
        displayed = losses.head(15)
        worst = losses.loc[losses["Profit"].idxmin()]
        fig = px.scatter(displayed, x="Sales", y="Profit", size="Sales", color="Profit", hover_name="City", color_continuous_scale="RdYlGn",
                         title="Top 15 Cities with High Sales but Negative Profit", labels={"Sales": "Total Sales ($)", "Profit": "Total Profit ($)"})
        fig.add_annotation(x=worst["Sales"], y=worst["Profit"], text=worst["City"], showarrow=True, arrowhead=2, bgcolor="#fef3c7")
        style_figure(fig, 590)
        show_chart(fig)
        show_insights([f"{worst['City']} has the lowest total profit among loss-making cities ({money(worst['Profit'])}).",
                       f"The chart retains only negative-profit cities, sorts them by sales, and displays the top 15."])


def question12(data: pd.DataFrame) -> None:
    question = "What is the relationship between sales and profit across all orders?"
    with st.container():
        section_header(12, question)
        if data.empty or show_empty(): return
        highest = data.loc[data["Profit"].idxmax()]
        fig = px.scatter(data, x="Sales", y="Profit", color="Category", opacity=0.7, color_discrete_sequence=SAFE_COLORS,
                         title="Relationship Between Sales and Profit Across All Orders",
                         labels={"Sales": "Sales ($)", "Profit": "Profit ($)", "Category": "Product Category"},
                         hover_data=["Order ID", "Customer Name", "Sub-Category"])
        fig.add_annotation(x=highest["Sales"], y=highest["Profit"], text="Highest Profit", showarrow=True, arrowhead=2, bgcolor="#fef3c7")
        style_figure(fig, 620)
        show_chart(fig)
        show_insights([f"The highest-profit order records {money(highest['Profit'])} in profit on {money(highest['Sales'])} in sales.",
                       "Each point represents an order line, coloured by product category as in the notebook."])


def data_extras(data: pd.DataFrame) -> None:
    """Provide requested filtered-data download, preview, dimensions, and null summary."""
    with st.expander("Dataset details and filtered data", expanded=False):
        col1, col2 = st.columns(2)
        col1.metric("Filtered rows", f"{data.shape[0]:,}")
        col2.metric("Columns", f"{data.shape[1]:,}")
        download_data = data.drop(columns=["Year", "Delivery Days"], errors="ignore")
        st.download_button("Download filtered dataset (CSV)", download_data.to_csv(index=False).encode("utf-8"), "filtered_global_superstore.csv", "text/csv")
        st.markdown("**Missing values summary**")
        missing = data.isna().sum().rename("Missing values").reset_index()
        missing.columns = ["Column", "Missing values"]
        st.dataframe(missing[missing["Missing values"] > 0], use_container_width=True, hide_index=True)
        st.markdown("**Raw data preview**")
        st.dataframe(download_data.head(100), use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Global Superstore Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
    st.markdown("""<style>
        .block-container {padding-top: 2rem; padding-bottom: 3rem;}
        .kpi-card {min-height: 122px; padding: 1.25rem; border-radius: 0.8rem; color: #ffffff !important; box-shadow: 0 6px 18px rgba(15, 23, 42, 0.18);}
        .kpi-label {font-size: 0.95rem; font-weight: 700; color: #ffffff !important; opacity: 0.92;}
        .kpi-value {margin-top: 0.55rem; font-size: 2rem; font-weight: 750; line-height: 1.15; color: #ffffff !important; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
        .kpi-card.sales {background: linear-gradient(135deg, #0369a1, #0ea5e9);}
        .kpi-card.profit {background: linear-gradient(135deg, #047857, #22c55e);}
        .kpi-card.orders {background: linear-gradient(135deg, #b45309, #f59e0b);}
        .kpi-card.customers {background: linear-gradient(135deg, #6d28d9, #a855f7);}
        .kpi-spacer {height: 1rem;}
        [data-testid=\"stPlotlyChart\"] {border-radius: 0.65rem;}
    </style>""", unsafe_allow_html=True)
    data = load_data()
    filtered = create_sidebar(data)
    st.session_state["filtered_rows"] = len(filtered)

    st.title("Global Superstore Performance Dashboard")
    st.caption("An interactive business analysis of sales, profit, customers, products, markets, and shipping performance.")
    st.markdown(f"**Dataset overview:** {len(data):,} transaction records across {data['Country'].nunique():,} countries and {data['Order Date'].min():%b %Y}–{data['Order Date'].max():%b %Y}.")
    display_kpis(filtered)
    st.markdown('<div class="kpi-spacer"></div>', unsafe_allow_html=True)
    data_extras(filtered)
    st.divider()

    left, right = st.columns(2, gap="large")
    with left:
        question1(filtered)
    with right:
        question2(filtered)
    st.divider()

    left, right = st.columns(2, gap="large")
    with left:
        question3(filtered)
    with right:
        question4(filtered)
    st.divider()

    left, right = st.columns(2, gap="large")
    with left:
        question5(filtered)
    with right:
        question6(filtered)
    st.divider()

    left, right = st.columns(2, gap="large")
    with left:
        question7(filtered)
    with right:
        question8(filtered)
    st.divider()

    question9(filtered)
    st.divider()
    question10(filtered)
    st.divider()

    left, right = st.columns(2, gap="large")
    with left:
        question11(filtered)
    with right:
        question12(filtered)


if __name__ == "__main__":
    main()
