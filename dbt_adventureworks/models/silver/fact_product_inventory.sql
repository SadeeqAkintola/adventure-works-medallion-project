{{
    config(
        materialized = "table",
        partition_by = {
            "field": "movement_date",
            "data_type": "date",
            "granularity": "month"
        },
        cluster_by = ["product_key"]
    )
}}

with raw_inventory as (
    select * from {{ source('bronze', 'FactProductInventory') }}
),

cleaned as (
    select
        cast(ProductKey as INT64) as product_key,
        cast(DateKey as INT64) as date_key,
        cast(MovementDate as DATE) as movement_date,
        cast(UnitCost as NUMERIC) as unit_cost,
        cast(UnitsIn as INT64) as units_in,
        cast(UnitsOut as INT64) as units_out,
        cast(UnitsBalance as INT64) as units_balance,
        round(cast(UnitsBalance as INT64) * cast(UnitCost as NUMERIC), 4) as inventory_valuation,

        -- Audit
        _ingested_at as bronze_ingested_at,
        current_timestamp() as silver_updated_at
    from raw_inventory
)

select * from cleaned
