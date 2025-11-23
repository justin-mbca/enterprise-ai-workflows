
        
            delete from "data"."main_marts"."events_incremental"
            where (
                event_id) in (
                select (event_id)
                from "events_incremental__dbt_tmp20251122190936185022"
            );

        
    

    insert into "data"."main_marts"."events_incremental" ("event_id", "event_type", "related_entity_id", "entity_type", "event_metadata", "event_timestamp", "event_date", "event_hour")
    (
        select "event_id", "event_type", "related_entity_id", "entity_type", "event_metadata", "event_timestamp", "event_date", "event_hour"
        from "events_incremental__dbt_tmp20251122190936185022"
    )
  