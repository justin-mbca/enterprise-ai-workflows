-- Document index mart combining all domains
WITH hr AS (
  SELECT policy_id AS id, category AS domain, raw_text AS text FROM {{ ref('stg_hr_policy') }}
), arb AS (
  SELECT doc_id AS id, category AS domain, raw_text AS text FROM {{ ref('stg_arbitration_subrogation') }}
), ml AS (
  SELECT concept_id AS id, topic AS domain, raw_text AS text FROM {{ ref('stg_ml_concepts') }}
), unioned AS (
  SELECT * FROM hr
  UNION ALL
  SELECT * FROM arb
  UNION ALL
  SELECT * FROM ml
)
SELECT * FROM unioned
