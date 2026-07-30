# Global Superstore Performance Dashboard

An interactive Streamlit dashboard that transforms the Global Superstore data-visualization assignment into a polished business analytics application. It preserves the notebook's original calculations, aggregations, and twelve business questions while adding interactive filtering, responsive Plotly charts, KPI cards, and downloadable data.

## Features

- Twelve dedicated business-analysis sections, maintained in the original notebook order
- Interactive filters for market, region, country, category, sub-category, segment, ship mode, and year
- Headline KPIs for total sales, total profit, unique orders, and unique customers
- Responsive Plotly visualizations with tooltips, zoom, pan, and image download controls
- Downloadable filtered dataset in CSV format
- Raw data preview, dataset dimensions, and missing-values summary
- Consistent, business-focused visual design suitable for portfolio presentation

## Business Questions

1. Which regions generate the highest sales and profit?
2. How has monthly sales changed over time across different markets?
3. Which product categories are most profitable?
4. Does offering higher discounts actually increase profit?
5. Which sub-categories generate high sales but low profit?
6. Which customer segments are the most profitable across markets?
7. Which countries have high sales but poor profit margins?
8. How does shipping mode affect delivery performance and profit?
9. What are the Top 15 most profitable products?
10. How do sales and profit vary across months and categories?
11. Which cities consistently generate losses despite high sales?
12. What is the relationship between sales and profit across all orders?

## Dataset

The application uses `Global_Superstore2.csv`, a transaction-level Global Superstore dataset stored in the project root. It includes order, customer, product, geographic, shipping, sales, discount, and profit information.

The dashboard reads the dataset locally and does not require external data access.

## Technologies Used

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/python/)

## Installation

1. Clone the repository and move into the project folder.

   ```bash
   git clone <your-repository-url>
   cd Naiya
   ```

2. Create and activate a virtual environment (recommended).

   ```bash
   python -m venv .venv
   ```

   **Windows PowerShell**

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**

   ```bash
   source .venv/bin/activate
   ```

3. Install the required packages.

   ```bash
   pip install -r requirements.txt
   ```

## How to Run

Ensure `Global_Superstore2.csv` remains in the same folder as `app.py`, then run:

```bash
streamlit run app.py
```

Streamlit will open the dashboard in your browser, usually at `http://localhost:8501`.

## Streamlit Community Cloud Deployment

1. Push this project to a GitHub repository.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select **New app**, then choose the repository, branch, and `app.py` as the main file.
4. Click **Deploy**.

No configuration changes are required, provided `Global_Superstore2.csv` and `requirements.txt` are included in the repository root.

## Folder Structure

```text
Naiya/
├── app.py                    # Streamlit dashboard
├── Global_Superstore2.csv    # Source dataset
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── dv-final.ipynb            # Original analysis notebook
└── Copy_of_dv_project.ipynb  # Original analysis notebook copy
```

## Screenshots

_Add dashboard screenshots here after running the application._

## Author

Built as a Streamlit implementation of the Global Superstore data-visualization assignment.
