-- Arbitration timelines mart
WITH base AS (
  SELECT * FROM {{ ref('stg_arbitration_subrogation') }}
), extracted AS (
  SELECT
    doc_id,
    category,
    raw_text,
    CASE WHEN raw_text LIKE '%90 days%' THEN 90 END AS hearing_target_days,
    CASE WHEN raw_text LIKE '%180 days%' THEN 180 END AS appeal_window_days,
    CASE WHEN raw_text LIKE '%one year%' THEN 365 END AS filing_deadline_days
  FROM base
)
SELECT * FROM extracted
