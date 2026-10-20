
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "sales.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "key_findings.txt"


def main():
    if not DATA_FILE.exists():
        print(f"Dataset not found: {DATA_FILE}")
        print("Make sure sales.csv is inside the data folder.")
        return

    # Load the dataset
    df = pd.read_csv(DATA_FILE, encoding="latin1")
    df.columns = df.columns.str.strip()

    required = ["Sales", "Profit"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        print("Missing required columns:", missing)
        print("Available columns:", df.columns.tolist())
        return

    # Clean numeric fields
    for col in ["Sales", "Profit", "Quantity", "Discount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Sales"] = df["Sales"].fillna(0)
    df["Profit"] = df["Profit"].fillna(0)

    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_rows = len(df)

    if "Order ID" in df.columns:
        total_orders = df["Order ID"].nunique()
    else:
        total_orders = total_rows

    total_units = (
        df["Quantity"].sum()
        if "Quantity" in df.columns
        else None
    )

    profit_margin = (
        total_profit / total_sales * 100
        if total_sales != 0
        else 0
    )

    findings = [
        "RETAIL SALES ANALYTICS — KEY FINDINGS",
        "=" * 45,
        "",
        "OVERALL PERFORMANCE",
        f"Total sales: ${total_sales:,.2f}",
        f"Total profit: ${total_profit:,.2f}",
        f"Unique orders: {total_orders:,}",
        f"Data rows: {total_rows:,}",
        f"Overall profit margin: {profit_margin:.2f}%",
    ]

    if total_units is not None:
        findings.append(f"Units sold: {total_units:,.0f}")

    # 1. Best-selling category
    if "Category" in df.columns:
        category_sales = (
            df.groupby("Category")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )

        if not category_sales.empty:
            best = category_sales.index[0]
            findings += [
                "",
                "1. TOP CATEGORY BY SALES",
                f"{best}: ${category_sales.iloc[0]:,.2f}",
            ]

    # 2. Most profitable region
    if {"Region", "Profit"}.issubset(df.columns):
        region_profit = (
            df.groupby("Region")["Profit"]
            .sum()
            .sort_values(ascending=False)
        )

        if not region_profit.empty:
            best = region_profit.index[0]
            findings += [
                "",
                "2. MOST PROFITABLE REGION",
                f"{best}: ${region_profit.iloc[0]:,.2f} profit",
            ]

    # 3. Best month by sales
    date_col = next(
        (c for c in ["Order Date", "Date"] if c in df.columns),
        None
    )

    if date_col:
        df[date_col] = pd.to_datetime(
            df[date_col], errors="coerce"
        )

        monthly = df.dropna(subset=[date_col]).copy()
        monthly["Month"] = monthly[date_col].dt.to_period("M")

        monthly_sales = monthly.groupby("Month")["Sales"].sum()

        if not monthly_sales.empty:
            best_month = monthly_sales.idxmax()
            findings += [
                "",
                "3. MONTH WITH HIGHEST SALES",
                f"{best_month}: ${monthly_sales.max():,.2f}",
            ]

            if len(monthly_sales) >= 2:
                first_month = monthly_sales.index.min()
                last_month = monthly_sales.index.max()

                findings += [
                    f"First month in data: {first_month}",
                    f"Last month in data: {last_month}",
                ]

    # 4. Product with highest sales
    if "Product Name" in df.columns:
        product_sales = (
            df.groupby("Product Name")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )

        if not product_sales.empty:
            findings += [
                "",
                "4. TOP PRODUCT BY SALES",
                f"{product_sales.index[0]}",
                f"Sales: ${product_sales.iloc[0]:,.2f}",
            ]

    # 5. Discount and profit relationship
    if {"Discount", "Profit"}.issubset(df.columns):
        valid = df[["Discount", "Profit"]].dropna()

        if len(valid) >= 2 and valid["Discount"].nunique() > 1:
            correlation = valid["Discount"].corr(valid["Profit"])

            findings += [
                "",
                "5. DISCOUNT AND PROFIT RELATIONSHIP",
                f"Pearson correlation: {correlation:.3f}",
                (
                    "Negative association in this dataset."
                    if correlation < 0
                    else "Positive association in this dataset."
                    if correlation > 0
                    else "No linear association in this dataset."
                ),
                "Correlation does not prove that discounts cause changes in profit.",
            ]

            discount_profit = (
                df.dropna(subset=["Discount", "Profit"])
                .groupby("Discount")
                .agg(
                    Average_Profit=("Profit", "mean"),
                    Records=("Profit", "size"),
                )
                .sort_index()
            )

            findings += [
                "",
                "AVERAGE PROFIT BY DISCOUNT LEVEL",
            ]

            for discount, row in discount_profit.iterrows():
                findings.append(
                    f"{discount:.0%} discount: "
                    f"${row['Average_Profit']:,.2f} average profit "
                    f"({int(row['Records'])} records)"
                )

    findings += [
        "",
        "NOTE",
        "These findings describe the supplied dataset only.",
        "They do not establish causation or guarantee future performance.",
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(findings), encoding="utf-8")

    print("\n".join(findings))
    print(f"\nFindings saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
