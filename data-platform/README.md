# Data Platform Extension

This directory adds a lightweight data engineering / analytics foundation to the existing enterprise AI workflows project.

## Components

| Layer | Tool | Purpose |
|-------|------|---------|
| Storage (local) | DuckDB | File-based analytical store for seeds & models |
| Transform | dbt Core + duckdb adapter | Declarative SQL transformations, tests, docs |
| Orchestration (free) | GitHub Actions | Scheduled & push-triggered pipeline (dbt run + tests + embedding refresh) |
| Vector Refresh | Python script (`scripts/refresh_embeddings.py`) | Rebuild RAG index from curated models |
| Serving (RAG) | Gradio app (`project3-document-qa/app.py`) | Answers questions over embedded curated corpus |
| Analytics | Streamlit dashboard (`analytics_dashboard.py`) | BI exploration of marts & document index |

## Structure
```
data-platform/
  dbt/
    dbt_project.yml
    profiles_template.yml
    seeds/                # Source CSVs (HR, Legal, ML concepts)
    models/
      staging/            # Raw cleaned staging tables
      marts/              # Domain & RAG mart tables
      models/schema.yml   # Tests & documentation
  README.md               # This file
scripts/
  refresh_embeddings.py   # Placeholder embedding refresh
```

## Running Locally (End-to-End)

Prerequisites: Python 3.11+, `pip install dbt-core dbt-duckdb duckdb sentence-transformers chromadb streamlit`.

```bash
# 1. Copy profile template (first time)
mkdir -p ~/.dbt
cp data-platform/dbt/profiles_template.yml ~/.dbt/profiles.yml

# 2. Install Python dependencies (data platform + embeddings + dashboard)
pip install -r data-platform/requirements.txt
pip install -r project3-document-qa/requirements.txt

# 3. Build curated data (dbt)
cd data-platform/dbt
dbt seed && dbt run && dbt test

# 4. Rebuild vector store from document_index mart
cd ../../
python scripts/refresh_embeddings.py --persist-dir project3-document-qa/chroma_store --reset

# 5. Launch RAG app (auto-detects persistent store)
cd project3-document-qa
python app.py  # http://localhost:7860

# 6. Launch analytics dashboard (BI on marts)
cd ../data-platform
streamlit run analytics_dashboard.py  # http://localhost:8502
```

Artifacts:
- DuckDB warehouse: `data-platform/dbt/warehouse/data.duckdb`
- Persistent embeddings: `project3-document-qa/chroma_store/`
- Dashboard code: `data-platform/analytics_dashboard.py`

To regenerate embeddings after data changes:
```bash
cd data-platform/dbt
dbt seed && dbt run
cd ../../
python scripts/refresh_embeddings.py --persist-dir project3-document-qa/chroma_store --reset
```

## GitHub Actions
Workflow: `.github/workflows/dbt-daily.yml`
1. Install dbt + dependencies
2. Run `dbt seed`, `dbt run`, `dbt test`
3. Generate docs (`dbt docs generate`)
4. (Next) Publish docs to GitHub Pages
5. (Future) Invoke `scripts/refresh_embeddings.py` and sync Space

## Next Enhancements
- dbt metrics & semantic layer for KPI standardization
- Extend Great Expectations / semantic checks beyond `document_index` (additional marts)
- Automated embedding refresh in CI (Space sync)
- Vector reranking (e.g., Cohere / cross-encoder) for improved relevance
- Lightdash or Evidence for advanced BI consumption

## One-Command Full Pipeline (Data → Quality → Embeddings)
For daily development or quick demos you can execute the entire sequence (dbt seed/run/test → semantic quality validations → embedding refresh → verification) with a single script at repo root:

```bash
./scripts/run_full_pipeline.sh
```

What it does:
1. Builds all seeds and models (staging + marts) using the local DuckDB profile (`data-platform/dbt/profiles.yml`).
2. Executes all dbt tests (structural quality: not_null, unique, relationships, accepted_values).
3. Runs semantic data checks (row count bounds, schema conformity, uniqueness, length ranges) acting as a lightweight Great Expectations gate.
4. Rebuilds the persistent Chroma vector store from the curated `document_index` mart.
5. Verifies embedding count matches document count.

Sample (abridged) output:
```
📥 STEP 1: dbt seed            ✅ Seeds loaded (3)
🏗️  STEP 2: dbt run             ✅ 6 models built
🧪 STEP 3: dbt test            ✅ 18 tests passed
🔍 STEP 4: Quality Gate        ✅ All semantic checks passed
🧬 STEP 5: Refresh Embeddings  ✅ 21 embeddings stored
✔️  STEP 6: Verify Vector Store ✅ 21 documents
🎉 PIPELINE COMPLETE!
```

Artifacts produced automatically:
- `data-platform/dbt/warehouse/data.duckdb`
- `project3-document-qa/chroma_store/` (persistent embeddings)
- `data-platform/dbt/target/` (dbt docs & manifest)

When to use script vs manual steps:
- Use the script for rapid iteration, demos, or CI reproducibility.
- Use manual steps when debugging a specific phase (e.g., only re-running `dbt test`).

Interview talking point:
> "I implemented a one-command pipeline that embeds structural (dbt) and semantic validations before generating embeddings—ensuring high-integrity data flows into the AI layer."

CI Integration (optional): A GitHub Actions workflow (`full-pipeline.yml`) can invoke this script on push + cron and publish artifacts for inspection.

## Why DuckDB?
DuckDB offers zero configuration, versionable analytical artifacts, and works well in CI. For a cloud warehouse variant, the same models can target Postgres or BigQuery with profile changes.

## Data Lineage
Use `dbt docs` for lineage: `seeds → staging → marts → document_index → embeddings (Chroma) → RAG app & dashboard`.

## License & Reuse
This structure is a starter template for integrating an analytical semantic layer with both:
1. RAG pipelines (embedding refresh from curated marts)
2. BI dashboards (Streamlit analytics on mart outputs)

Adaptable to cloud warehouses by swapping the profile (e.g., Postgres, BigQuery) without rewriting models.
