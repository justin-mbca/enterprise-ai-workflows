
    
    

with child as (
    select policy_id as from_field
    from "data"."main_marts"."hr_policy_features"
    where policy_id is not null
),

parent as (
    select policy_id as to_field
    from "data"."main_staging"."stg_hr_policy"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


