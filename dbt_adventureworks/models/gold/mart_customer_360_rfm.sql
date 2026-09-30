{{
    config(
        materialized = "table",
        cluster_by = ["customer_segment", "country_name", "income_tier"]
    )
}}

with customer_base as (
    select * from {{ ref('dim_customers') }}
),

orders as (
    select
        customer_key,
        order_date,
        sales_order_number,
        sales_amount,
        gross_profit,
        order_quantity
    from {{ ref('fact_internet_sales') }}
),

-- Reference date for RFM recency calculation
reference_date as (
    select coalesce(max(order_date), current_date()) as max_order_date
    from orders
),

customer_aggregates as (
    select
        o.customer_key,
        count(distinct o.sales_order_number) as lifetime_orders,
        sum(o.order_quantity) as lifetime_units_purchased,
        sum(o.sales_amount) as lifetime_spend,
        sum(o.gross_profit) as lifetime_profit_generated,
        round(safe_divide(sum(o.sales_amount), count(distinct o.sales_order_number)), 2) as average_order_value,
        min(o.order_date) as first_order_date,
        max(o.order_date) as latest_order_date,
        date_diff(max(r.max_order_date), max(o.order_date), DAY) as days_since_last_purchase,
        date_diff(max(o.order_date), min(o.order_date), DAY) as customer_tenure_days
    from orders o
    cross join reference_date r
    group by o.customer_key
),

rfm_scoring as (
    select
        c.*,
        a.lifetime_orders,
        a.lifetime_units_purchased,
        coalesce(a.lifetime_spend, 0) as lifetime_spend,
        coalesce(a.lifetime_profit_generated, 0) as lifetime_profit_generated,
        a.average_order_value,
        a.first_order_date,
        a.latest_order_date,
        a.days_since_last_purchase,
        a.customer_tenure_days,
        
        -- RFM Quintile Scoring (1 to 5)
        ntile(5) over (order by a.days_since_last_purchase desc) as r_score,
        ntile(5) over (order by a.lifetime_orders asc) as f_score,
        ntile(5) over (order by a.lifetime_spend asc) as m_score
    from customer_base c
    inner join customer_aggregates a
        on c.customer_key = a.customer_key
),

rfm_segmented as (
    select
        *,
        concat(cast(r_score as STRING), cast(f_score as STRING), cast(m_score as STRING)) as rfm_cell,
        case
            when r_score >= 4 and f_score >= 4 and m_score >= 4 then 'Champions'
            when r_score >= 3 and f_score >= 3 and m_score >= 3 then 'Loyal Customers'
            when r_score >= 4 and f_score <= 2 then 'Promising / New Customers'
            when r_score >= 3 and f_score <= 2 and m_score >= 3 then 'Potential Loyalists'
            when r_score <= 2 and f_score >= 3 and m_score >= 3 then 'At Risk / Need Attention'
            when r_score <= 1 and f_score >= 4 and m_score >= 4 then 'Cannot Lose Them'
            when r_score <= 2 and f_score <= 2 then 'Hibernating / Lost'
            else 'Standard Customers'
        end as customer_segment
    from rfm_scoring
)

select * from rfm_segmented
