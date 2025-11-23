select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with all_values as (

    select
        category as value_field,
        count(*) as n_records

    from "data"."main_staging"."stg_hr_policy"
    group by category

)

select *
from all_values
where value_field not in (
    'PTO','Overtime','Payroll','Benefits','FMLA','Expense','Performance'
)



      
    ) dbt_internal_test