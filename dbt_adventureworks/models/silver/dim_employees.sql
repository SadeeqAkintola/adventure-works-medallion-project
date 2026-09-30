{{
    config(
        materialized = "table",
        cluster_by = ["department_name", "sales_person_flag", "status"]
    )
}}

with raw_employees as (
    select * from {{ source('bronze', 'DimEmployee') }}
),

cleaned as (
    select
        cast(EmployeeKey as INT64) as employee_key,
        cast(ParentEmployeeKey as INT64) as manager_employee_key,
        trim(EmployeeNationalIDAlternateKey) as national_id,
        cast(SalesTerritoryKey as INT64) as sales_territory_key,
        trim(FirstName) as first_name,
        nullif(trim(MiddleName), '') as middle_name,
        trim(LastName) as last_name,
        concat(trim(FirstName), ' ', coalesce(concat(trim(MiddleName), ' '), ''), trim(LastName)) as full_name,
        trim(Title) as job_title,
        cast(HireDate as DATE) as hire_date,
        cast(BirthDate as DATE) as birth_date,
        lower(trim(EmailAddress)) as email_address,
        trim(Phone) as phone_number,
        case 
            when MaritalStatus = 'M' then 'Married'
            when MaritalStatus = 'S' then 'Single'
            else 'Unknown'
        end as marital_status,
        case 
            when Gender = 'M' then 'Male'
            when Gender = 'F' then 'Female'
            else 'Unknown'
        end as gender,
        case when SalariedFlag = true or SalariedFlag = '1' then true else false end as is_salaried,
        cast(BaseRate as NUMERIC) as base_rate,
        cast(VacationHours as INT64) as vacation_hours,
        cast(SickLeaveHours as INT64) as sick_leave_hours,
        case when CurrentFlag = true or CurrentFlag = '1' then true else false end as is_current_employee,
        case when SalesPersonFlag = true or SalesPersonFlag = '1' then true else false end as sales_person_flag,
        coalesce(trim(DepartmentName), 'General') as department_name,
        cast(StartDate as DATE) as department_start_date,
        cast(EndDate as DATE) as department_end_date,
        coalesce(trim(Status), case when EndDate is null then 'Active' else 'Departed' end) as status,

        -- Audit
        _ingested_at as bronze_ingested_at,
        current_timestamp() as silver_updated_at
    from raw_employees
)

select * from cleaned
