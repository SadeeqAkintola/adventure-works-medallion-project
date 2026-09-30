{{
    config(
        materialized = "table",
        partition_by = {
            "field": "entry_date",
            "data_type": "date",
            "granularity": "month"
        },
        cluster_by = ["account_type", "scenario_name", "department_group_name"]
    )
}}

with ledger as (
    select * from {{ ref('fact_finance_ledger') }}
),

accounts as (
    select
        cast(AccountKey as INT64) as account_key,
        trim(AccountDescription) as account_description,
        trim(AccountType) as account_type
    from {{ source('bronze', 'DimAccount') }}
),

departments as (
    select
        cast(DepartmentGroupKey as INT64) as department_group_key,
        trim(DepartmentGroupName) as department_group_name
    from {{ source('bronze', 'DimDepartmentGroup') }}
),

scenarios as (
    select
        cast(ScenarioKey as INT64) as scenario_key,
        trim(ScenarioName) as scenario_name
    from {{ source('bronze', 'DimScenario') }}
),

organizations as (
    select
        cast(OrganizationKey as INT64) as organization_key,
        trim(OrganizationName) as organization_name
    from {{ source('bronze', 'DimOrganization') }}
),

joined as (
    select
        l.finance_key,
        l.entry_date,
        extract(year from l.entry_date) as entry_year,
        extract(quarter from l.entry_date) as entry_quarter,
        extract(month from l.entry_date) as entry_month,
        
        -- Dimensions
        coalesce(a.account_description, 'General Ledger') as account_description,
        coalesce(a.account_type, 'General') as account_type,
        coalesce(d.department_group_name, 'Corporate') as department_group_name,
        coalesce(o.organization_name, 'AdventureWorks Global') as organization_name,
        coalesce(s.scenario_name, 'Actual') as scenario_name,
        
        -- Amounts
        l.amount
    from ledger l
    left join accounts a on l.account_key = a.account_key
    left join departments d on l.department_group_key = d.department_group_key
    left join organizations o on l.organization_key = o.organization_key
    left join scenarios s on l.scenario_key = s.scenario_key
)

select * from joined
