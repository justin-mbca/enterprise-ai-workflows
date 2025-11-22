# Analytics Dashboard

Simple Streamlit dashboard consuming dbt mart tables for business intelligence.

## Features

- **Overview**: Total documents, domain distribution
- **HR Policies**: PTO accrual, overtime mentions, payroll cycles
- **Arbitration**: Filing deadline analysis
- **Document Index**: RAG corpus explorer with export options

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure dbt models are built
cd dbt
dbt seed && dbt run
cd ..

# Launch dashboard
streamlit run analytics_dashboard.py
```

The dashboard will open at `http://localhost:8501`

## Data Sources

Queries the following dbt marts from `dbt/warehouse/data.duckdb`:
- `main_marts.document_index` - Unified document corpus (21 docs)
- `main_marts.hr_policy_features` - HR policy feature flags (7 policies)
- `main_marts.arbitration_timelines` - Extracted filing deadlines (7 docs)

## Screenshots

**Overview Tab**: Document distribution across domains (HR, Legal, ML)

**HR Policies Tab**: 
- Metrics: PTO policies, overtime mentions, payroll cycles
- Category breakdown chart
- Feature flags table

**Arbitration Tab**:
- Average/min/max filing deadlines
- Deadline distribution chart

**Document Index Tab**:
- Filter by domain
- Export as CSV/JSON
- Preview text snippets

## Refresh Data

Click the "🔄 Refresh Data" button to reload after running `dbt run`.

## Use Cases

- Portfolio demonstration of BI skills
- Interview talking points (dbt → analytics pipeline)
- Quick data validation after dbt runs
- Export curated data for other tools
