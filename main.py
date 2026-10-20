
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Project folders
DATA_FILE = "data/sales.csv"
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_FILE, encoding="latin1")

print("=" * 50)
print("       RETAIL SALES ANALYSIS")
print("=" * 50)

# Clean column names
df.columns = df.columns.str.strip()

# Convert dates where available
for col in df.columns:
    if "date" in col.lower():
        df[col] = pd.to_datetime(df[col], errors="coerce")

print("\nDataset shape:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())

print("\nMissing values before cleaning:")
print(df.isnull().sum())

# Remove duplicate records
df = df.drop_duplicates()

# Identify relevant columns
sales_col = next(
    (c for c in df.columns if c.lower() == "sales"), None
)
profit_col = next(
    (c for c in df.columns if c.lower() == "profit"), None
)
category_col = next(
    (c for c in df.columns if c.lower() == "category"), None
)
region_col = next(
    (c for c in df.columns if c.lower() == "region"), None
)
product_col = next(
    (c for c in df.columns if c.lower() == "product name"), None
)

if sales_col is None:
    raise ValueError("Could not find a Sales column in the CSV.")

# Summary statistics
total_sales = df[sales_col].sum()
print(f"\nTotal Sales: {total_sales:,.2f}")

if profit_col:
    total_profit = df[profit_col].sum()
    print(f"Total Profit: {total_profit:,.2f}")
    print(f"Profit Margin: {(total_profit / total_sales * 100):.2f}%"
          if total_sales else "Profit Margin: N/A")

print(f"Total Records: {len(df):,}")

# Sales by category
if category_col:
    category_sales = df.groupby(category_col)[sales_col].sum()
    print("\nSales by Category:")
    print(category_sales.sort_values(ascending=False))

    plt.figure(figsize=(9, 5))
    category_sales.sort_values().plot(kind="barh")
    plt.title("Total Sales by Category")
    plt.xlabel("Sales")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/sales_by_category.png", dpi=150)
    plt.close()

# Sales by region
if region_col:
    region_sales = df.groupby(region_col)[sales_col].sum()
    print("\nSales by Region:")
    print(region_sales.sort_values(ascending=False))

    plt.figure(figsize=(9, 5))
    region_sales.sort_values().plot(kind="barh")
    plt.title("Total Sales by Region")
    plt.xlabel("Sales")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/sales_by_region.png", dpi=150)
    plt.close()

# Top 10 products by sales
if product_col:
    top_products = (
        df.groupby(product_col)[sales_col]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    print("\nTop 10 Products by Sales:")
    print(top_products)

    plt.figure(figsize=(10, 6))
    top_products.sort_values().plot(kind="barh")
    plt.title("Top 10 Products by Sales")
    plt.xlabel("Sales")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/top_10_products.png", dpi=150)
    plt.close()

# Save cleaned data and report
df.to_csv(f"{OUTPUT_DIR}/cleaned_sales.csv", index=False)

with open(f"{OUTPUT_DIR}/summary_report.txt", "w", encoding="utf-8") as report:
    report.write("RETAIL SALES ANALYSIS SUMMARY\n")
    report.write("=" * 35 + "\n")
    report.write(f"Total records: {len(df):,}\n")
    report.write(f"Total sales: {total_sales:,.2f}\n")
    if profit_col:
        report.write(f"Total profit: {total_profit:,.2f}\n")

print(f"\nAnalysis complete! Check the '{OUTPUT_DIR}' folder.")
