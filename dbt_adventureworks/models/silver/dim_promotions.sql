{{
    config(
        materialized = "table",
        cluster_by = ["promotion_category", "promotion_type"]
    )
}}

with raw_promotions as (
    select * from {{ source('bronze', 'DimPromotion') }}
),

cleaned as (
    select
        cast(PromotionKey as INT64) as promotion_key,
        cast(PromotionAlternateKey as INT64) as promotion_id,
        trim(EnglishPromotionName) as promotion_name,
        cast(DiscountPct as FLOAT64) as discount_pct,
        coalesce(trim(EnglishPromotionType), 'Regular') as promotion_type,
        coalesce(trim(EnglishPromotionCategory), 'Standard') as promotion_category,
        cast(StartDate as TIMESTAMP) as start_date,
        cast(EndDate as TIMESTAMP) as end_date,
        cast(MinQty as INT64) as min_quantity,
        cast(MaxQty as INT64) as max_quantity,

        -- Audit
        _ingested_at as bronze_ingested_at,
        current_timestamp() as silver_updated_at
    from raw_promotions
)

select * from cleaned
