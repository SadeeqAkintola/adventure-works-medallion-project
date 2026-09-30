{{
    config(
        materialized = "table",
        cluster_by = ["category_name", "subcategory_name", "product_line"]
    )
}}

with raw_products as (
    select * from {{ source('bronze', 'DimProduct') }}
),

raw_subcategories as (
    select * from {{ source('bronze', 'DimProductSubcategory') }}
),

raw_categories as (
    select * from {{ source('bronze', 'DimProductCategory') }}
),

cleaned as (
    select
        cast(p.ProductKey as INT64) as product_key,
        trim(p.ProductAlternateKey) as product_sku,
        cast(p.ProductSubcategoryKey as INT64) as product_subcategory_key,
        trim(p.EnglishProductName) as product_name,
        coalesce(trim(p.ProductLine), 'Standard') as product_line,
        coalesce(trim(p.Color), 'Multi/NA') as color,
        coalesce(trim(p.Size), 'NA') as size,
        nullif(trim(p.SizeRange), '') as size_range,
        cast(p.Weight as FLOAT64) as weight,
        cast(p.StandardCost as NUMERIC) as standard_cost,
        cast(p.ListPrice as NUMERIC) as list_price,
        cast(p.DealerPrice as NUMERIC) as dealer_price,
        case 
            when cast(p.ListPrice as NUMERIC) > 0 
            then round((cast(p.ListPrice as NUMERIC) - cast(p.StandardCost as NUMERIC)) / cast(p.ListPrice as NUMERIC) * 100, 2)
            else 0.0
        end as standard_margin_pct,
        cast(p.SafetyStockLevel as INT64) as safety_stock_level,
        cast(p.ReorderPoint as INT64) as reorder_point,
        cast(p.DaysToManufacture as INT64) as days_to_manufacture,
        case when p.FinishedGoodsFlag = true or p.FinishedGoodsFlag = '1' then true else false end as is_finished_goods,
        coalesce(trim(p.Class), 'NA') as product_class,
        coalesce(trim(p.Style), 'NA') as product_style,
        coalesce(trim(p.ModelName), 'Unassigned') as model_name,
        cast(p.StartDate as TIMESTAMP) as valid_from,
        cast(p.EndDate as TIMESTAMP) as valid_to,
        coalesce(trim(p.Status), case when p.EndDate is null then 'Current' else 'Discontinued' end) as product_status,

        -- Category & Subcategory hierarchies
        coalesce(s.EnglishProductSubcategoryName, 'Uncategorized') as subcategory_name,
        coalesce(c.EnglishProductCategoryName, 'Uncategorized') as category_name,

        -- Audit
        p._ingested_at as bronze_ingested_at,
        current_timestamp() as silver_updated_at
    from raw_products p
    left join raw_subcategories s
        on cast(p.ProductSubcategoryKey as INT64) = cast(s.ProductSubcategoryKey as INT64)
    left join raw_categories c
        on cast(s.ProductCategoryKey as INT64) = cast(c.ProductCategoryKey as INT64)
)

select * from cleaned
