{{
    config(
        materialized = "table",
        partition_by = {
            "field": "order_date",
            "data_type": "date",
            "granularity": "month"
        },
        cluster_by = ["sales_channel", "category_name", "territory_country"]
    )
}}

with internet_sales as (
    select
        s.sales_order_number,
        s.sales_order_line_number,
        s.order_date,
        s.order_quantity,
        s.unit_price,
        s.extended_amount,
        s.discount_amount,
        s.total_product_cost,
        s.sales_amount,
        s.tax_amount,
        s.freight_amount,
        s.gross_profit,
        s.sales_channel,
        s.product_key,
        s.sales_territory_key,
        s.customer_key,
        cast(null as INT64) as reseller_key,
        cast(null as INT64) as employee_key
    from {{ ref('fact_internet_sales') }} s
),

reseller_sales as (
    select
        s.sales_order_number,
        s.sales_order_line_number,
        s.order_date,
        s.order_quantity,
        s.unit_price,
        s.extended_amount,
        s.discount_amount,
        s.total_product_cost,
        s.sales_amount,
        s.tax_amount,
        s.freight_amount,
        s.gross_profit,
        s.sales_channel,
        s.product_key,
        s.sales_territory_key,
        cast(null as INT64) as customer_key,
        s.reseller_key,
        s.employee_key
    from {{ ref('fact_reseller_sales') }} s
),

unioned_sales as (
    select * from internet_sales
    union all
    select * from reseller_sales
),

products as (
    select * from {{ ref('dim_products') }}
),

territories as (
    select * from {{ ref('dim_sales_territories') }}
),

joined as (
    select
        u.sales_order_number,
        u.sales_order_line_number,
        u.order_date,
        extract(year from u.order_date) as order_year,
        extract(quarter from u.order_date) as order_quarter,
        extract(month from u.order_date) as order_month,
        format_date('%Y-%m', u.order_date) as year_month,
        u.sales_channel,
        
        -- Product Hierarchies
        p.product_sku,
        p.product_name,
        p.category_name,
        p.subcategory_name,
        p.product_line,
        p.model_name,
        
        -- Territory Hierarchies
        coalesce(t.territory_country, 'Unassigned') as territory_country,
        coalesce(t.territory_region, 'Unassigned') as territory_region,
        coalesce(t.territory_group, 'Unassigned') as territory_group,
        
        -- Metrics
        u.order_quantity,
        u.unit_price,
        u.extended_amount,
        u.discount_amount,
        u.sales_amount as gross_sales_amount,
        (u.sales_amount - u.discount_amount) as net_sales_amount,
        u.total_product_cost as cogs_amount,
        u.gross_profit,
        case 
            when u.sales_amount > 0 
            then round(safe_divide(u.gross_profit, u.sales_amount) * 100, 2)
            else 0.0
        end as gross_margin_pct,
        u.tax_amount,
        u.freight_amount
    from unioned_sales u
    left join products p
        on u.product_key = p.product_key
    left join territories t
        on u.sales_territory_key = t.sales_territory_key
)

select * from joined
