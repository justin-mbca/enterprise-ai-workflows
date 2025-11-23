select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select category
from "data"."main_staging"."stg_arbitration_subrogation"
where category is null



      
    ) dbt_internal_test