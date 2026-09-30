# AdventureWorks DW Medallion Data Dictionary

## Silver Models (`adventureworks_silver`)

### 1. `dim_customers`
- **Grain**: One record per individual customer (`customer_key`).
- **Cluster Keys**: `[geography_key, education_level, occupation]`
- **Key Columns**:
  - `customer_key` (`INT64`, PK): Unique surrogate key.
  - `customer_id` (`STRING`): Natural business key (e.g. `AW00011000`).
  - `full_name` (`STRING`): Customer first and last name.
  - `yearly_income` (`NUMERIC`): Declared annual income.
  - `income_tier` (`STRING`): Categorical income bracket (`Low`, `Middle`, `Upper-Middle`, `High`).
  - `education_level` (`STRING`): Highest education attainment.
  - `occupation` (`STRING`): Occupation role.
  - `city`, `state_province`, `country_name` (`STRING`): Geography attributes.

### 2. `dim_products`
- **Grain**: One record per product (`product_key`).
- **Cluster Keys**: `[category_name, subcategory_name, product_line]`
- **Key Columns**:
  - `product_key` (`INT64`, PK): Unique surrogate key.
  - `product_sku` (`STRING`): Business SKU.
  - `product_name` (`STRING`): Cleaned product name.
  - `category_name` (`STRING`): Top-level category (`Bikes`, `Components`, `Clothing`, `Accessories`).
  - `subcategory_name` (`STRING`): Subcategory rollup (e.g., `Mountain Bikes`, `Road Frames`).
  - `standard_cost` (`NUMERIC`): Standard manufacturing/acquisition cost.
  - `list_price` (`NUMERIC`): Retail list price.
  - `standard_margin_pct` (`FLOAT64`): Calculated retail margin percentage.

### 3. `dim_resellers`
- **Grain**: One record per B2B partner/reseller (`reseller_key`).
- **Cluster Keys**: `[business_type, country_name, order_frequency]`
- **Key Columns**:
  - `reseller_key` (`INT64`, PK): Unique surrogate key.
  - `reseller_name` (`STRING`): Reseller partner name.
  - `business_type` (`STRING`): Partner type (`Warehouse`, `Value Added Reseller`, `Specialty Bike Shop`).
  - `annual_sales`, `annual_revenue` (`NUMERIC`): Stated business volume.

### 4. `fact_internet_sales`
- **Grain**: One record per line item of an e-commerce order (`sales_order_line_id`).
- **Partitioning**: `order_date` (MONTH)
- **Cluster Keys**: `[customer_key, product_key, sales_territory_key]`
- **Key Columns**:
  - `sales_order_line_id` (`STRING`, PK): Unique concatenated order and line item ID.
  - `order_date` (`DATE`): Date order was placed.
  - `order_quantity` (`INT64`): Units ordered.
  - `sales_amount` (`NUMERIC`): Gross sales revenue.
  - `total_product_cost` (`NUMERIC`): Cost of goods sold (COGS).
  - `gross_profit` (`NUMERIC`): `sales_amount - total_product_cost`.

### 5. `fact_reseller_sales`
- **Grain**: One record per line item of a B2B reseller order (`sales_order_line_id`).
- **Partitioning**: `order_date` (MONTH)
- **Cluster Keys**: `[reseller_key, product_key, employee_key]`
- **Key Columns**:
  - `sales_order_line_id` (`STRING`, PK): Unique order line ID.
  - `reseller_key` (`INT64`): Foreign key to `dim_resellers`.
  - `employee_key` (`INT64`): Foreign key to `dim_employees` (Sales Rep).
  - `sales_amount` (`NUMERIC`): Total wholesale transaction amount.

---

## Gold Analytical Marts (`adventureworks_gold`)

### 1. `mart_sales_executive_overview`
- **Target Persona**: Executive & Commercial Leadership.
- **Grain**: One record per sales order line item across both Internet and Reseller channels.
- **Partitioning**: `order_date` (MONTH)
- **Cluster Keys**: `[sales_channel, category_name, territory_country]`
- **Calculated Metrics**:
  - `gross_sales_amount`: Total revenue.
  - `net_sales_amount`: Revenue net of promotions/discounts.
  - `cogs_amount`: Total cost of goods sold.
  - `gross_profit`: Net sales minus COGS.
  - `gross_margin_pct`: Profit margin percentage.

### 2. `mart_customer_360_rfm`
- **Target Persona**: Marketing & Growth Analytics.
- **Grain**: One record per customer (`customer_key`).
- **Cluster Keys**: `[customer_segment, country_name, income_tier]`
- **Calculated Metrics**:
  - `lifetime_orders`: Total distinct orders placed.
  - `lifetime_spend`: Total monetary spend ($).
  - `days_since_last_purchase`: Recency in days.
  - `r_score`, `f_score`, `m_score`: RFM quintile scores (1 to 5).
  - `customer_segment`: Assigned segment (`Champions`, `Loyal Customers`, `Potential Loyalists`, `At Risk`, `Lost`).

### 3. `mart_inventory_supply_chain`
- **Target Persona**: Supply Chain & Operations.
- **Grain**: Daily inventory snapshot per product.
- **Partitioning**: `movement_date` (MONTH)
- **Cluster Keys**: `[category_name, stock_health_status, product_sku]`
- **Calculated Metrics**:
  - `units_balance`: Current on-hand quantity.
  - `inventory_valuation`: Ending inventory value (`units_balance * unit_cost`).
  - `stock_health_status`: `Stockout`, `Below Reorder Point`, `Safety Stock Warning`, `Optimal Stock`, `Overstocked`.
  - `is_reorder_triggered`: Boolean flag indicating replenishment need.

### 4. `mart_sales_rep_quota_performance`
- **Target Persona**: Sales Leadership & Account Executives.
- **Grain**: Quarterly quota vs actual sales performance per sales representative.
- **Cluster Keys**: `[calendar_year, calendar_quarter, sales_rep_name]`
- **Calculated Metrics**:
  - `target_quota`: Quarterly quota goal ($).
  - `actual_sales_amount`: Total reseller sales revenue closed.
  - `quota_attainment_pct`: `(actual_sales / target_quota) * 100`.
  - `performance_bracket`: `Quota Achieved`, `Near Target (80-99%)`, `Under Target (<80%)`.

### 5. `mart_finance_pnl_summary`
- **Target Persona**: Finance & FP&A Leadership.
- **Grain**: Monthly general ledger entries across departments and accounts.
- **Partitioning**: `entry_date` (MONTH)
- **Cluster Keys**: `[account_type, scenario_name, department_group_name]`
- **Calculated Metrics**:
  - `amount`: Financial transaction amount.
  - `scenario_name`: `Actual` vs `Budget` vs `Forecast`.
  - `department_group_name`: Corporate department rollup.
