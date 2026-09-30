{{
    config(
        materialized = "table",
        cluster_by = ["employee_key", "calendar_year", "calendar_quarter"]
    )
}}

with raw_quota as (
    select * from {{ source('bronze', 'FactSalesQuota') }}
),

cleaned as (
    select
        cast(SalesQuotaKey as INT64) as sales_quota_key,
        cast(EmployeeKey as INT64) as employee_key,
        cast(DateKey as INT64) as date_key,
        cast(CalendarYear as INT64) as calendar_year,
        cast(CalendarQuarter as INT64) as calendar_quarter,
        cast(SalesAmountQuota as NUMERIC) as sales_amount_quota,
        cast(Date as DATE) as quota_date,

        -- Audit
        _ingested_at as bronze_ingested_at,
        current_timestamp() as silver_updated_at
    from raw_quota
)

select * from cleaned
