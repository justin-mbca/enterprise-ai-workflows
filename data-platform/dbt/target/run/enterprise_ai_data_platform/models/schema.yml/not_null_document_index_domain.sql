select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select domain
from "data"."main_marts"."document_index"
where domain is null



      
    ) dbt_internal_test