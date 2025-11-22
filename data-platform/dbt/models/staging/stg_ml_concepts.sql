-- Staging model for ML concepts seed
WITH source AS (
  SELECT * FROM {{ ref('ml_concepts') }}
)
SELECT
  concept_id,
  topic,
  text AS raw_text,
  LENGTH(text) AS text_length,
  CURRENT_TIMESTAMP AS ingested_at
FROM source
