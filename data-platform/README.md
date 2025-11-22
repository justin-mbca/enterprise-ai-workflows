# Data Platform Extension

This directory adds a lightweight data engineering / analytics foundation to the existing enterprise AI workflows project.

## Components

| Layer | Tool | Purpose |
|-------|------|---------|
| Storage (local) | DuckDB | File-based analytical store for seeds & models |
| Transform | dbt Core + duckdb adapter | Declarative SQL transformations, tests, docs |
| Orchestration (free) | GitHub Actions | Scheduled & push-triggered pipeline (dbt run + tests + embedding refresh) |
| Vector Refresh | Python script (`scripts/refresh_embeddings.py`) | Rebuild RAG index from curated models |
| Serving | Existing Streamlit / Gradio apps | Consume curated features & documents |

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

## Running Locally

Prerequisites: Python 3.11+, `pip install dbt-core dbt-duckdb duckdb`.

```bash
# 1. Copy profile template (first time)
mkdir -p ~/.dbt
cp data-platform/dbt/profiles_template.yml ~/.dbt/profiles.yml

# 2. Install packages
pip install dbt-core dbt-duckdb duckdb

# 3. Run pipeline
cd data-platform/dbt
dbt seed
dbt run
dbt test

# 4. Inspect docs locally
# (Generate docs site)
dbt docs generate
# (Serve the site)
dbt docs serve

# 5. Embedding refresh (placeholder)
python ../../scripts/refresh_embeddings.py
```

## GitHub Actions (Planned)
A workflow `.github/workflows/dbt-daily.yml` will:
1. Install dbt + dependencies.
2. Execute `dbt seed/run/test`.
3. Generate docs and publish to GitHub Pages.
4. Call `refresh_embeddings.py`.
5. (Optional) Upload updated project3 RAG folder to Hugging Face Space.

## Next Enhancements
- Add metrics layer (dbt metrics spec).
- Introduce Great Expectations for deeper data validation.
- Streamlit Metrics Explorer page reading DuckDB outputs.
- Reranking model integration in RAG pipeline.

## Why DuckDB?
DuckDB offers zero configuration, versionable analytical artifacts, and works well in CI. For a cloud warehouse variant, the same models can target Postgres or BigQuery with profile changes.

## Data Lineage
Use `dbt docs` to visualize lineage: seeds -> staging -> marts -> unified document_index consumed by RAG embedding refresh.

## License & Reuse
This structure can be transplanted as a starter data platform for prototypes needing a governed semantic layer feeding LLM or analytical applications.
