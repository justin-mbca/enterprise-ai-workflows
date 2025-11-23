
  
  create view "data"."main_staging"."stg_ml_concepts__dbt_tmp" as (
    -- Staging model for ML concepts seed
WITH source AS (
  SELECT * FROM "data"."main"."ml_concepts"
)
SELECT
  concept_id,
  topic,
  text AS raw_text,
  LENGTH(text) AS text_length,
  CURRENT_TIMESTAMP AS ingested_at
FROM source
  );
