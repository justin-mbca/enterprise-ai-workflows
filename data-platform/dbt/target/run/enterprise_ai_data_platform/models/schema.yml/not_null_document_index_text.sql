select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select text
from "data"."main_marts"."document_index"
where text is null



      
    ) dbt_internal_test