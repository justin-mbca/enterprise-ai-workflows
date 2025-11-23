select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select id
from "data"."main_marts"."document_index"
where id is null



      
    ) dbt_internal_test