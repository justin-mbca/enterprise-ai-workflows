
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select accrual_days_per_month as from_field
    from "data"."main_marts"."hr_policy_features"
    where accrual_days_per_month is not null
),

parent as (
    select policy_id as to_field
    from stg_hr_policy
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test