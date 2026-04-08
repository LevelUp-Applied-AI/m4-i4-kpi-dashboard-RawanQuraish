import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from scipy import stats

sns.set_palette('colorblind')


def connect_db():
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/amman_market"
    )
    engine = create_engine(database_url)
    return engine


def extract_data(engine):
    customers_df = pd.read_sql("SELECT * FROM customers;", engine)
    products_df = pd.read_sql("SELECT * FROM products;", engine)
    orders_df = pd.read_sql("SELECT * FROM orders WHERE status != 'cancelled';", engine)
    order_items_df = pd.read_sql("SELECT * FROM order_items WHERE quantity <= 100;", engine)
    
    return {
        "customers": customers_df,
        "products": products_df,
        "orders": orders_df,
        "order_items": order_items_df
    }


def compute_kpis(data_dict):
    orders = data_dict['orders']
    order_items = data_dict['order_items']
    products = data_dict['products']
    customers = data_dict['customers']

    # Merge data for calculations
    merged = order_items.merge(orders, on='order_id', how='left')
    merged = merged.merge(products, on='product_id', how='left')
    merged = merged.merge(customers[['customer_id']], on='customer_id', how='left')

    # --- KPI 1: Monthly Revenue ---
    merged['month'] = pd.to_datetime(merged['order_date']).dt.to_period('M')
    monthly_revenue = merged.groupby('month').apply(lambda x: (x['quantity'] * x['unit_price']).sum())

    # --- KPI 2: Weekly Order Volume ---
    merged['week'] = pd.to_datetime(merged['order_date']).dt.to_period('W')
    weekly_orders = merged.groupby('week')['order_id'].nunique()

    # --- KPI 3: Average Order Value by Product Category ---
    aov_category = merged.groupby('category').apply(
        lambda x: (x['quantity'] * x['unit_price']).sum() / x['order_id'].nunique()
    ).reset_index().rename(columns={0:'avg_order_value'})

    # --- KPI 4: Customer Retention Rate (monthly) ---
    monthly_customers = merged.groupby('month')['customer_id'].nunique()
    returning_customers = merged[merged.duplicated(['customer_id'], keep=False)]
    monthly_returning = returning_customers.groupby('month')['customer_id'].nunique()
    retention_rate = (monthly_returning / monthly_customers * 100).fillna(0)

    # --- KPI 5: Top Selling Products ---
    top_products = merged.groupby('product_name')['quantity'].sum().sort_values(ascending=False).head(10)
    top_products = top_products.reset_index().rename(columns={'quantity':'total_quantity'})

    return {
        'monthly_revenue': monthly_revenue,
        'weekly_orders': weekly_orders,
        'aov_by_category': aov_category,
        'customer_retention': retention_rate,
        'top_products': top_products
    }


def run_statistical_tests(data_dict):
    merged = data_dict['order_items'].merge(data_dict['orders'], on='order_id', how='left')
    merged = merged.merge(data_dict['products'], on='product_id', how='left')

    # Test: Does AOV differ across product categories? -> ANOVA
    category_groups = [group['quantity']*group['unit_price'] for name, group in merged.groupby('category')]
    f_stat, p_value = stats.f_oneway(*category_groups)
    interpretation = "Reject H0" if p_value < 0.05 else "Fail to reject H0"

    return {
        'anova_aov_category': {
            'H0': 'Average order value is the same across categories',
            'H1': 'Average order value differs across categories',
            'f_stat': f_stat,
            'p_value': p_value,
            'interpretation': interpretation
        }
    }


def create_visualizations(kpi_results, stat_results):
    sns.set_palette('colorblind')
    
    # --- Multi-panel figure: Monthly Revenue + Weekly Orders ---
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    kpi_results['monthly_revenue'].plot(ax=axes[0], kind='line', marker='o', color='tab:blue')
    axes[0].set_title("Monthly Revenue Trend")
    axes[0].set_ylabel("Revenue (JOD)")
    axes[0].grid(True)

    kpi_results['weekly_orders'].plot(ax=axes[1], kind='line', marker='s', color='tab:green')
    axes[1].set_title("Weekly Order Volume")
    axes[1].set_ylabel("Number of Orders")
    axes[1].grid(True)

    plt.tight_layout()
    plt.savefig("output/multi_panel_time_based.png")
    plt.close()

    # --- Boxplot: Average Order Value by Product Category ---
    plt.figure(figsize=(10,6))
    sns.boxplot(
        x='category', 
        y='avg_order_value', 
        data=kpi_results['aov_by_category']
    )
    plt.title("Average Order Value by Product Category")
    plt.xlabel("Product Category")
    plt.ylabel("Average Order Value (JOD)")
    plt.savefig("output/aov_boxplot.png")
    plt.close()

    # --- Bar chart: Top Selling Products ---
    plt.figure(figsize=(12,6))
    sns.barplot(
        x='product_name',
        y='total_quantity',
        data=kpi_results['top_products']
    )
    plt.title("Top Selling Products (Quantity Sold)")
    plt.xlabel("Product")
    plt.ylabel("Quantity Sold")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig("output/top_products.png")
    plt.close()

    # --- Line chart: Customer Retention Rate ---
    plt.figure(figsize=(10,6))
    kpi_results['customer_retention'].plot(kind='line', marker='o', color='tab:orange')
    plt.title("Customer Retention Rate Over Time")
    plt.xlabel("Month")
    plt.ylabel("Retention Rate (%)")
    plt.grid(True)
    plt.savefig("output/customer_retention.png")
    plt.close()

    print("All KPI visualizations saved to output/ folder.")


def main():
    os.makedirs("output", exist_ok=True)
    engine = connect_db()
    data_dict = extract_data(engine)
    kpi_results = compute_kpis(data_dict)
    stat_results = run_statistical_tests(data_dict)
    create_visualizations(kpi_results, stat_results)

    print("=== KPI Summary ===")
    for k, v in kpi_results.items():
        print(f"{k}:\n{v}\n")

    print("=== Statistical Test Summary ===")
    for test, result in stat_results.items():
        print(f"{test}:")
        for k, val in result.items():
            print(f"{k}: {val}")
        print()


if __name__ == "__main__":
    main()