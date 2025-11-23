select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select policy_id
from "data"."main_staging"."stg_hr_policy"
where policy_id is null



      
    ) dbt_internal_test