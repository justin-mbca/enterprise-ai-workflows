-- Staging model for arbitration & subrogation seed
WITH source AS (
  SELECT * FROM "data"."main"."arbitration_subrogation"
)
SELECT
  doc_id,
  category,
  text AS raw_text,
  LENGTH(text) AS text_length,
  CURRENT_TIMESTAMP AS ingested_at
FROM source