-- Staging model for HR policy seed
WITH source AS (
  SELECT * FROM {{ source('seed_data', 'hr_policy') }}
)
SELECT
  policy_id,
  category,
  text AS raw_text,
  LENGTH(text) AS text_length,
  CURRENT_TIMESTAMP AS ingested_at
FROM source
