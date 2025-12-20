
    
    

select
    policy_id as unique_field,
    count(*) as n_records

from "data"."main_staging"."stg_hr_policy"
where policy_id is not null
group by policy_id
having count(*) > 1


