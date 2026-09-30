{{
    config(
        materialized = "table"
    )
}}

with raw_territories as (
    select * from {{ source('bronze', 'DimSalesTerritory') }}
),

cleaned as (
    select
        cast(SalesTerritoryKey as INT64) as sales_territory_key,
        cast(SalesTerritoryAlternateKey as INT64) as sales_territory_id,
        trim(SalesTerritoryRegion) as territory_region,
        trim(SalesTerritoryCountry) as territory_country,
        trim(SalesTerritoryGroup) as territory_group,
        
        -- Audit
        _ingested_at as bronze_ingested_at,
        current_timestamp() as silver_updated_at
    from raw_territories
)

select * from cleaned
