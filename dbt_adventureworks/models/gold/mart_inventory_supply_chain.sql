{{
    config(
        materialized = "table",
        partition_by = {
            "field": "movement_date",
            "data_type": "date",
            "granularity": "month"
        },
        cluster_by = ["category_name", "stock_health_status", "product_sku"]
    )
}}

with inventory_daily as (
    select * from {{ ref('fact_product_inventory') }}
),

products as (
    select * from {{ ref('dim_products') }}
),

enriched as (
    select
        inv.movement_date,
        inv.product_key,
        p.product_sku,
        p.product_name,
        p.category_name,
        p.subcategory_name,
        p.product_line,
        p.safety_stock_level,
        p.reorder_point,
        inv.unit_cost,
        inv.units_in,
        inv.units_out,
        inv.units_balance,
        inv.inventory_valuation,

        -- Stock Health Evaluation
        case
            when inv.units_balance <= 0 then 'Stockout'
            when inv.units_balance < p.reorder_point then 'Below Reorder Point'
            when inv.units_balance < p.safety_stock_level then 'Safety Stock Warning'
            when inv.units_balance > (p.safety_stock_level * 3) then 'Overstocked'
            else 'Optimal Stock'
        end as stock_health_status,

        case when inv.units_balance < p.reorder_point then true else false end as is_reorder_triggered
    from inventory_daily inv
    inner join products p
        on inv.product_key = p.product_key
)

select * from enriched
