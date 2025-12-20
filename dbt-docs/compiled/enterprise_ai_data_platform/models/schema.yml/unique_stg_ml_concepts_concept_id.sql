
    
    

select
    concept_id as unique_field,
    count(*) as n_records

from "data"."main_staging"."stg_ml_concepts"
where concept_id is not null
group by concept_id
having count(*) > 1


