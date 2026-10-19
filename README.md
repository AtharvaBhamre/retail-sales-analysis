# Retail Sales Analysis Dashboard

## Project Overview
Retail Sales Analysis is a Python-based data analytics project that explores retail transaction data to identify sales trends, profitability patterns, and regional performance. It uses an interactive dashboard to present business insights through charts, KPIs, and filters.

## Objectives
- Analyze total sales, profit, quantity, and profit margin.
- Identify the best-performing product categories and regions.
- Explore monthly sales trends.
- Examine the relationship between discounts and profitability.
- Present findings through an interactive dashboard.

## Technologies Used
- Python
- Pandas and NumPy
- Plotly
- Streamlit
- CSV dataset

## Features
- Interactive sales dashboard
- Key performance indicators (KPIs)
- Sales and profit visualizations
- Date, region, category, and segment filters
- Top-performing product analysis
- Data table and CSV export

## Dataset
The project uses a retail sales CSV dataset containing order details, products, customer segments, geographical information, sales, discounts, and profit.

## How to Run
1. Install Python.
2. Install the required packages using `python -m pip install -r requirements.txt`.
3. Place `sales.csv` inside the `data` folder.
4. Run `python -m streamlit run dashboard.py`.
5. Open the local URL displayed in the terminal.

## Key Findings
- Total sales: approximately $2.30 million.
- Total profit: approximately $286,397.
- Technology was the highest-sales category.
- The West region generated the highest profit.
- Higher discounts showed a negative relationship with profit in the dataset.

## Future Improvements
- Add sales forecasting.
- Add customer segmentation.
- Deploy the dashboard online.
- Improve dashboard styling and mobile responsiveness.
