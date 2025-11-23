{{ config(
    materialized='incremental',
    unique_key='event_id',
    on_schema_change='fail'
) }}

/*
    Incremental events model demonstrating scalability pattern.
    
    In a production setting this would capture:
    - User interactions (RAG queries, dashboard page views)
    - System events (pipeline runs, validation results)
    - Audit trail for governance
    
    For portfolio purposes, this is a synthetic example showing:
    - is_incremental() logic
    - Unique key constraint
    - Timestamp-based filtering
    - Schema evolution handling
*/

with base_events as (
    select
        -- Synthetic event generation for demo purposes
        'evt_' || cast(row_number() over (order by policy_id) as varchar) as event_id,
        'policy_view' as event_type,
        policy_id as related_entity_id,
        'hr_policy' as entity_type,
        category as event_metadata,
        current_timestamp as event_timestamp
    from {{ ref('stg_hr_policy') }}
    
    {% if is_incremental() %}
    -- Only process new records on incremental runs
    where current_timestamp > (select max(event_timestamp) from {{ this }})
    {% endif %}
),

events_with_attributes as (
    select
        event_id,
        event_type,
        related_entity_id,
        entity_type,
        event_metadata,
        event_timestamp,
        date_trunc('day', event_timestamp) as event_date,
        date_trunc('hour', event_timestamp) as event_hour
    from base_events
)

select * from events_with_attributes
