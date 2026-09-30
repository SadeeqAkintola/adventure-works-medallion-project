{{
    config(
        materialized = "table",
        cluster_by = ["geography_key", "education_level", "occupation"]
    )
}}

with raw_customers as (
    select * from {{ source('bronze', 'DimCustomer') }}
),

raw_geography as (
    select * from {{ source('bronze', 'DimGeography') }}
),

cleaned as (
    select
        cast(c.CustomerKey as INT64) as customer_key,
        cast(c.GeographyKey as INT64) as geography_key,
        coalesce(c.CustomerAlternateKey, 'UNKNOWN') as customer_id,
        nullif(trim(c.Title), '') as title,
        trim(c.FirstName) as first_name,
        nullif(trim(c.MiddleName), '') as middle_name,
        trim(c.LastName) as last_name,
        concat(trim(c.FirstName), ' ', coalesce(concat(trim(c.MiddleName), ' '), ''), trim(c.LastName)) as full_name,
        case when c.NameStyle = true or c.NameStyle = '1' then true else false end as is_eastern_name_order,
        cast(c.BirthDate as DATE) as birth_date,
        case 
            when c.MaritalStatus = 'M' then 'Married'
            when c.MaritalStatus = 'S' then 'Single'
            else 'Unknown'
        end as marital_status,
        case 
            when c.Gender = 'M' then 'Male'
            when c.Gender = 'F' then 'Female'
            else 'Unknown'
        end as gender,
        lower(trim(c.EmailAddress)) as email_address,
        cast(c.YearlyIncome as NUMERIC) as yearly_income,
        case
            when cast(c.YearlyIncome as NUMERIC) < 30000 then 'Low Income (<$30k)'
            when cast(c.YearlyIncome as NUMERIC) between 30000 and 70000 then 'Middle Income ($30k-$70k)'
            when cast(c.YearlyIncome as NUMERIC) between 70001 and 100000 then 'Upper-Middle ($70k-$100k)'
            when cast(c.YearlyIncome as NUMERIC) > 100000 then 'High Income (>$100k)'
            else 'Unspecified'
        end as income_tier,
        cast(c.TotalChildren as INT64) as total_children,
        cast(c.NumberChildrenAtHome as INT64) as children_at_home,
        coalesce(c.EnglishEducation, 'Unknown') as education_level,
        coalesce(c.EnglishOccupation, 'Unknown') as occupation,
        case when c.HouseOwnerFlag = '1' or c.HouseOwnerFlag = true then true else false end as is_homeowner,
        cast(c.NumberCarsOwned as INT64) as cars_owned,
        trim(c.AddressLine1) as address_line1,
        nullif(trim(c.AddressLine2), '') as address_line2,
        trim(c.Phone) as phone_number,
        cast(c.DateFirstPurchase as DATE) as date_first_purchase,
        coalesce(c.CommuteDistance, 'Unknown') as commute_distance,
        
        -- Joined Geography attributes
        g.City as city,
        g.StateProvinceName as state_province,
        g.CountryRegionCode as country_code,
        g.EnglishCountryRegionName as country_name,
        g.PostalCode as postal_code,
        cast(g.SalesTerritoryKey as INT64) as sales_territory_key,

        -- Ingestion audit
        c._ingested_at as bronze_ingested_at,
        current_timestamp() as silver_updated_at
    from raw_customers c
    left join raw_geography g
        on cast(c.GeographyKey as INT64) = cast(g.GeographyKey as INT64)
)

select * from cleaned
