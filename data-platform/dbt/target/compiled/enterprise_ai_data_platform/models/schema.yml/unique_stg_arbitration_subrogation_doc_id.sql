
    
    

select
    doc_id as unique_field,
    count(*) as n_records

from "data"."main_staging"."stg_arbitration_subrogation"
where doc_id is not null
group by doc_id
having count(*) > 1


