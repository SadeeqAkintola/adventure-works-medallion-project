{{
    config(
        materialized = "table",
        cluster_by = ["calendar_year", "calendar_quarter", "sales_rep_name"]
    )
}}

with quotas as (
    select * from {{ ref('fact_sales_quota') }}
),

employees as (
    select * from {{ ref('dim_employees') }}
    where sales_person_flag = true
),

reseller_sales as (
    select
        employee_key,
        extract(year from order_date) as order_year,
        extract(quarter from order_date) as order_quarter,
        sum(sales_amount) as actual_sales_amount,
        sum(gross_profit) as actual_gross_profit,
        count(distinct sales_order_number) as orders_closed
    from {{ ref('fact_reseller_sales') }}
    group by 1, 2, 3
),

performance as (
    select
        q.calendar_year,
        q.calendar_quarter,
        concat(cast(q.calendar_year as STRING), '-Q', cast(q.calendar_quarter as STRING)) as year_quarter,
        e.employee_key,
        e.full_name as sales_rep_name,
        e.job_title,
        e.department_name,
        e.email_address,
        q.sales_amount_quota as target_quota,
        coalesce(s.actual_sales_amount, 0) as actual_sales_amount,
        coalesce(s.actual_gross_profit, 0) as actual_gross_profit,
        coalesce(s.orders_closed, 0) as orders_closed,
        
        -- Quota Attainment Calculations
        case 
            when q.sales_amount_quota > 0 
            then round(safe_divide(coalesce(s.actual_sales_amount, 0), q.sales_amount_quota) * 100, 2)
            else 0.0
        end as quota_attainment_pct,
        
        (coalesce(s.actual_sales_amount, 0) - q.sales_amount_quota) as quota_variance_amount,
        
        case
            when coalesce(s.actual_sales_amount, 0) >= q.sales_amount_quota then 'Quota Achieved'
            when coalesce(s.actual_sales_amount, 0) >= (q.sales_amount_quota * 0.8) then 'Near Target (80-99%)'
            else 'Under Target (<80%)'
        end as performance_bracket
    from quotas q
    inner join employees e
        on q.employee_key = e.employee_key
    left join reseller_sales s
        on q.employee_key = s.employee_key
        and q.calendar_year = s.order_year
        and q.calendar_quarter = s.order_quarter
)

select * from performance
