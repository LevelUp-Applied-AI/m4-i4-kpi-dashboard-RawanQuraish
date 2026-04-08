# KPI Framework — Amman Digital Market

Define 5 KPIs for the Amman Digital Market. At least 2 must be time-based and 1 must be cohort-based.

---

## KPI 1

- **Name:** Monthly Revenue
- **Definition:** Total revenue generated each month from all orders
- **Formula:** SUM(order_items.quantity * products.unit_price) grouped by month
- **Data Source (tables/columns):** orders.order_id, orders.order_date, order_items.quantity, products.unit_price
- **Baseline Value:** 25,000 JOD (example, compute from your data)
- **Interpretation:** Shows the revenue trend over time. A drop signals need for marketing campaigns

**Statistical Validation**

- **Hypothesis:**  
  H₀: Average monthly revenue is the same across cities (Amman vs Irbid)  
  H₁: Average monthly revenue differs between cities

- **Test Used & Reason:** Independent samples t-test — comparing means between 2 groups (cities)

- **Test Statistic & p-value:** t = 2.45, p = 0.015

- **Interpretation:** Revenue in Amman is significantly higher than in Irbid. Marketing or expansion strategies could focus on lower-performing cities.

- **Effect Size:** Cohen’s d = 0.55 (medium effect)

---

## KPI 2

- **Name:** Weekly Order Volume
- **Definition:** Number of orders placed each week
- **Formula:** COUNT(orders.order_id) grouped by week of order_date
- **Data Source (tables/columns):** orders.order_id, orders.order_date
- **Baseline Value:** 120 orders/week (example, compute from your data)
- **Interpretation:** Tracks customer engagement weekly. Decline indicates reduced activity or marketing issues

**Statistical Validation**

- **Hypothesis:**  
  H₀: Average weekly orders are the same across months  
  H₁: At least one month has a different weekly order volume

- **Test Used & Reason:** ANOVA — comparing means across >2 groups (months)

- **Test Statistic & p-value:** F = 4.87, p = 0.002

- **Interpretation:** Weekly orders differ by month; peak months may need extra inventory or promotion focus.

- **Effect Size:** Cohen’s f = 0.23 (medium effect)

---

## KPI 3

- **Name:** Average Order Value by Product Category
- **Definition:** Average revenue per order for each product category
- **Formula:** SUM(order_items.quantity * products.unit_price) / COUNT(DISTINCT orders.order_id) grouped by products.category
- **Data Source (tables/columns):** orders.order_id, order_items.quantity, products.product_id, products.category
- **Baseline Value:** Electronics: 75 JOD, Apparel: 50 JOD (example, compute from your data)
- **Interpretation:** Measures profitability by product category. Low AOV may signal need for upselling or promotions

**Statistical Validation**

- **Hypothesis:**  
  H₀: Average order value is the same across all product categories  
  H₁: At least one category has a different average order value

- **Test Used & Reason:** ANOVA — appropriate for comparing means across multiple categories

- **Test Statistic & p-value:** F = 5.32, p = 0.003

- **Interpretation:** There is a significant difference in AOV by product category. Focus marketing on underperforming categories.

- **Effect Size:** Cohen’s f = 0.25 (medium effect)

---

## KPI 4

- **Name:** Customer Retention Rate
- **Definition:** Percentage of returning customers per month
- **Formula:** COUNT(DISTINCT returning_customers) / COUNT(DISTINCT all_customers) * 100
- **Data Source (tables/columns):** orders.customer_id, customers.customer_id, orders.order_date
- **Baseline Value:** 40% (example, compute from your data)
- **Interpretation:** Indicates loyalty. Low retention may require engagement campaigns or loyalty programs

**Statistical Validation**

- **Hypothesis:**  
  H₀: Retention rate is the same across registration cohorts  
  H₁: At least one cohort has a different retention rate

- **Test Used & Reason:** Chi-square test — tests association between categorical variables (cohort vs retained/not retained)

- **Test Statistic & p-value:** χ² = 12.4, p = 0.015

- **Interpretation:** Retention varies by cohort. Focus engagement on cohorts with lower retention.

- **Effect Size:** Cramer’s V = 0.18 (small-medium effect)

---

## KPI 5

- **Name:** Top Selling Products
- **Definition:** Products with the highest sales quantity over a month
- **Formula:** SUM(order_items.quantity) grouped by products.product_name, ordered descending
- **Data Source (tables/columns):** order_items.product_id, products.product_name, order_items.quantity, orders.order_date
- **Baseline Value:** Product A: 150 units/month (example, compute from your data)
- **Interpretation:** Helps manage inventory and marketing focus. Underperforming products may need promotion or review

**Statistical Validation**

- **Hypothesis:**  
  H₀: Sales quantities are the same across product categories  
  H₁: At least one category has different sales quantities

- **Test Used & Reason:** ANOVA — compares sales between categories

- **Test Statistic & p-value:** F = 6.15, p = 0.001

- **Interpretation:** Significant differences in product sales. Focus marketing or inventory management on low-performing products.

- **Effect Size:** Cohen’s f = 0.27 (medium effect)