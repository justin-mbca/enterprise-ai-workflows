select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select raw_text
from "data"."main_staging"."stg_arbitration_subrogation"
where raw_text is null



      
    ) dbt_internal_test