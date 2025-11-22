# Airflow Optional Orchestration Layer

This directory provides an OPTIONAL workflow orchestration layer to showcase proficiency with Apache Airflow for portfolio / interview purposes (e.g., Analytics / Data Engineering roles).

## Why It's Here
The base repo already runs fine with GitHub Actions + scripts. Airflow is added to demonstrate:
- Multi-step DAG modeling (dbt seed → run → test → embeddings → quality check)
- Data quality enforcement before downstream tasks
- Separation of transformation vs. semantic enrichment (embeddings)
- Potential for SLAs, retries, and backfills

## DAG: `data_platform_pipeline`
Located at `airflow/dags/data_platform_pipeline.py`
Tasks:
1. `dbt_seed` – Load seed CSVs into DuckDB
2. `dbt_run` – Build staging + marts (including `document_index`)
3. `dbt_test` – Enforce data quality (relationships, not_null, accepted_values)
4. `ge_document_index_validation` – Run Great Expectations checkpoint (schema, domain, text bounds, row count)
5. `refresh_embeddings` – Rebuild persistent Chroma store from `document_index`
6. `doc_vector_count_check` – Assert vector count matches document count

Schedule: Daily at 05:00 UTC (adjust `schedule_interval`).

**Data Quality Gate (NEW):** The GE task validates semantic contracts (domain in ["hr", "legal", "technical"], text length 50-20000 chars, no nulls). If validation fails, the pipeline stops before refreshing embeddings, preventing corrupted vector representations.

## Setup (Local Demo)
```bash
# From repo root
export AIRFLOW_HOME="$(pwd)/airflow"
python -m venv venv && source venv/bin/activate
pip install -r airflow/requirements-airflow.txt

# Initialize metadata DB
airflow db init

# Set required variables
airflow variables set REPO_ROOT "$(pwd)"
# (Optional) override embeddings directory
airflow variables set CHROMA_DIR "$(pwd)/project3-document-qa/chroma_store"

# Create a user (if not using standalone)
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin

# Start Airflow (simplest path)
airflow standalone  # combines webserver + scheduler
# UI: http://localhost:8080
```

## Backfill Example
If you later partition documents by date (e.g., daily ingestion), you can backfill last week:
```bash
airflow dags backfill data_platform_pipeline -s 2025-11-15 -e 2025-11-22
```

## Extending
Ideas:
- Add statistical distribution expectations (e.g., `expect_column_mean_to_be_between` for text length trends).
- Add branch for model retraining if embeddings changed > X%.
- Add Slack/email alert on test failures (use `EmailOperator` or provider hooks).
- Dynamic task mapping for multi-domain document ingestion.
- Add Great Expectations validation for other marts (`hr_policy_features`, `arbitration_timelines`).

## Notes
- Imports are guarded so the DAG file can exist without breaking non-Airflow environments.
- This layer is optional; keep CI scripts to show pragmatic use of lightweight scheduling.

## Removal
If you choose not to showcase Airflow, simply omit this folder from portfolio or reference GitHub Actions only.
