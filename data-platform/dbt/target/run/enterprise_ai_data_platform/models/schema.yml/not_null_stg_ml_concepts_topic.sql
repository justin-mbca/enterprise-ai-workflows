select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select topic
from "data"."main_staging"."stg_ml_concepts"
where topic is null



      
    ) dbt_internal_test