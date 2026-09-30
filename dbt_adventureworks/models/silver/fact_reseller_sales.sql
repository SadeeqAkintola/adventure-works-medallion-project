{{
    config(
        materialized = "table",
        partition_by = {
            "field": "order_date",
            "data_type": "date",
            "granularity": "month"
        },
        cluster_by = ["reseller_key", "product_key", "employee_key"]
    )
}}

with raw_sales as (
    select * from {{ source('bronze', 'FactResellerSales') }}
),

cleaned as (
    select
        trim(SalesOrderNumber) as sales_order_number,
        cast(SalesOrderLineNumber as INT64) as sales_order_line_number,
        concat(trim(SalesOrderNumber), '-', cast(SalesOrderLineNumber as STRING)) as sales_order_line_id,
        
        -- Keys
        cast(ProductKey as INT64) as product_key,
        cast(OrderDateKey as INT64) as order_date_key,
        cast(DueDateKey as INT64) as due_date_key,
        cast(ShipDateKey as INT64) as ship_date_key,
        cast(ResellerKey as INT64) as reseller_key,
        cast(EmployeeKey as INT64) as employee_key,
        cast(PromotionKey as INT64) as promotion_key,
        cast(CurrencyKey as INT64) as currency_key,
        cast(SalesTerritoryKey as INT64) as sales_territory_key,

        -- Transaction Dates
        cast(OrderDate as DATE) as order_date,
        cast(DueDate as DATE) as due_date,
        cast(ShipDate as DATE) as ship_date,

        -- Quantities & Financials
        cast(OrderQuantity as INT64) as order_quantity,
        cast(UnitPrice as NUMERIC) as unit_price,
        cast(ExtendedAmount as NUMERIC) as extended_amount,
        cast(UnitPriceDiscountPct as FLOAT64) as unit_price_discount_pct,
        cast(DiscountAmount as NUMERIC) as discount_amount,
        cast(ProductStandardCost as NUMERIC) as product_standard_cost,
        cast(TotalProductCost as NUMERIC) as total_product_cost,
        cast(SalesAmount as NUMERIC) as sales_amount,
        cast(TaxAmt as NUMERIC) as tax_amount,
        cast(Freight as NUMERIC) as freight_amount,

        -- Derived Metrics
        round(cast(SalesAmount as NUMERIC) - cast(TotalProductCost as NUMERIC), 4) as gross_profit,
        case 
            when cast(SalesAmount as NUMERIC) > 0 
            then round((cast(SalesAmount as NUMERIC) - cast(TotalProductCost as NUMERIC)) / cast(SalesAmount as NUMERIC) * 100, 2)
            else 0.0
        end as gross_profit_margin_pct,

        -- Channel identification
        'Reseller' as sales_channel,

        -- Audit
        _ingested_at as bronze_ingested_at,
        current_timestamp() as silver_updated_at
    from raw_sales
)

select * from cleaned
