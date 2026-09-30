{{
    config(
        materialized = "table",
        partition_by = {
            "field": "entry_date",
            "data_type": "date",
            "granularity": "month"
        },
        cluster_by = ["organization_key", "department_group_key", "account_key"]
    )
}}

with raw_finance as (
    select * from {{ source('bronze', 'FactFinance') }}
),

cleaned as (
    select
        cast(FinanceKey as INT64) as finance_key,
        cast(DateKey as INT64) as date_key,
        cast(OrganizationKey as INT64) as organization_key,
        cast(DepartmentGroupKey as INT64) as department_group_key,
        cast(ScenarioKey as INT64) as scenario_key,
        cast(AccountKey as INT64) as account_key,
        cast(Amount as NUMERIC) as amount,
        cast(Date as DATE) as entry_date,

        -- Audit
        _ingested_at as bronze_ingested_at,
        current_timestamp() as silver_updated_at
    from raw_finance
)

select * from cleaned
