-- HR policy features mart
WITH base AS (
  SELECT * FROM "data"."main_staging"."stg_hr_policy"
), enriched AS (
  SELECT
    policy_id,
    category,
    raw_text,
    CASE WHEN category = 'PTO' THEN 1.67 ELSE NULL END AS accrual_days_per_month,
    raw_text LIKE '%overtime%' AS mentions_overtime,
    raw_text LIKE '%bi-weekly%' AS mentions_payroll_cycle
  FROM base
)
SELECT * FROM enriched