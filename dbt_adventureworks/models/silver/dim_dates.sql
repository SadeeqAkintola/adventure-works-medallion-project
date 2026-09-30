{{
    config(
        materialized = "table",
        cluster_by = ["calendar_year", "calendar_quarter", "english_month_name"]
    )
}}

with raw_dates as (
    select * from {{ source('bronze', 'DimDate') }}
),

cleaned as (
    select
        cast(DateKey as INT64) as date_key,
        cast(FullDateAlternateKey as DATE) as full_date,
        cast(DayNumberOfWeek as INT64) as day_of_week_num,
        trim(EnglishDayNameOfWeek) as day_name,
        cast(DayNumberOfMonth as INT64) as day_of_month,
        cast(DayNumberOfYear as INT64) as day_of_year,
        cast(WeekNumberOfYear as INT64) as week_of_year,
        trim(EnglishMonthName) as english_month_name,
        cast(MonthNumberOfYear as INT64) as month_of_year,
        cast(CalendarQuarter as INT64) as calendar_quarter,
        cast(CalendarYear as INT64) as calendar_year,
        cast(CalendarSemester as INT64) as calendar_semester,
        cast(FiscalQuarter as INT64) as fiscal_quarter,
        cast(FiscalYear as INT64) as fiscal_year,
        cast(FiscalSemester as INT64) as fiscal_semester,
        concat(cast(CalendarYear as STRING), '-Q', cast(CalendarQuarter as STRING)) as year_quarter,
        concat(cast(CalendarYear as STRING), '-', lpad(cast(MonthNumberOfYear as STRING), 2, '0')) as year_month,
        case when cast(DayNumberOfWeek as INT64) in (1, 7) then true else false end as is_weekend
    from raw_dates
)

select * from cleaned
