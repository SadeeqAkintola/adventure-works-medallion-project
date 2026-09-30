{{
    config(
        materialized = "table",
        cluster_by = ["business_type", "country_name", "order_frequency"]
    )
}}

with raw_resellers as (
    select * from {{ source('bronze', 'DimReseller') }}
),

raw_geography as (
    select * from {{ source('bronze', 'DimGeography') }}
),

cleaned as (
    select
        cast(r.ResellerKey as INT64) as reseller_key,
        cast(r.GeographyKey as INT64) as geography_key,
        coalesce(trim(r.ResellerAlternateKey), 'UNKNOWN') as reseller_id,
        trim(r.ResellerName) as reseller_name,
        coalesce(trim(r.BusinessType), 'Unknown') as business_type,
        cast(r.NumberEmployees as INT64) as employee_count,
        coalesce(trim(r.OrderFrequency), 'Ad-Hoc') as order_frequency,
        cast(r.OrderMonth as INT64) as order_month,
        cast(r.FirstOrderYear as INT64) as first_order_year,
        cast(r.LastOrderYear as INT64) as last_order_year,
        coalesce(trim(r.ProductLine), 'Standard') as product_line,
        trim(r.AddressLine1) as address_line1,
        nullif(trim(r.AddressLine2), '') as address_line2,
        cast(r.AnnualSales as NUMERIC) as annual_sales,
        cast(r.AnnualRevenue as NUMERIC) as annual_revenue,
        trim(r.BankName) as bank_name,
        cast(r.YearOpened as INT64) as year_opened,
        trim(r.Phone) as phone_number,

        -- Geographic attributes
        g.City as city,
        g.StateProvinceName as state_province,
        g.CountryRegionCode as country_code,
        g.EnglishCountryRegionName as country_name,
        g.PostalCode as postal_code,
        cast(g.SalesTerritoryKey as INT64) as sales_territory_key,

        -- Audit
        r._ingested_at as bronze_ingested_at,
        current_timestamp() as silver_updated_at
    from raw_resellers r
    left join raw_geography g
        on cast(r.GeographyKey as INT64) = cast(g.GeographyKey as INT64)
)

select * from cleaned
