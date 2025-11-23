# 🚀 Enterprise AI Workflows - Free Implementation Guide

## Quick launch

<p>
  <a href="https://enterprise-ai-workflows-d3ds3rasntycg5bwaqru5a.streamlit.app">
    <img alt="Streamlit App" src="https://img.shields.io/badge/Project%201-Streamlit%20App-ff4b4b?logo=streamlit&logoColor=white">
  </a>
  <a href="https://zhangju2023-mlops-pipeline-demo.hf.space/mlflow/">
    <img alt="MLflow UI" src="https://img.shields.io/badge/Project%202-MLflow%20UI-0194E2">
  </a>
  <a href="https://zhangju2023-mlops-pipeline-demo.hf.space/api/docs">
    <img alt="API Docs" src="https://img.shields.io/badge/Project%202-API%20Docs-009688?logo=fastapi&logoColor=white">
  </a>
  <a href="https://zhangju2023-mlops-pipeline-demo.hf.space/api/health">
    <img alt="API Health" src="https://img.shields.io/badge/Project%202-Health-4caf50">
  </a>
  <a href="https://zhangju2023-mlops-pipeline-demo.hf.space/api/predict/example">
    <img alt="Example Prediction" src="https://img.shields.io/badge/Project%202-Example%20Prediction-7c4dff">
  </a>
  <a href="https://huggingface.co/spaces/zhangju2023/document-qa-rag">
    <img alt="RAG App" src="https://img.shields.io/badge/Project%203-RAG%20App-ffcc4d?logo=huggingface&logoColor=black">
  </a>
</p>

> Learn enterprise AI/ML workflows using **100% free and open-source tools**. Perfect for building your portfolio and preparing for interviews!

## 📋 Overview

This repository contains three production-ready projects that demonstrate enterprise AI/ML workflows without expensive licenses:

1. **Rapid Insights Workflow** - SQL-based analytics with AI capabilities
2. **Enterprise MLOps Pipeline** - Complete ML lifecycle management
3. **Document Q&A System** - RAG-based LLM application
4. **Data Platform & Analytics** - dbt-powered curated corpus + Streamlit dashboard feeding RAG & BI layers

## 🎯 What You'll Learn

- **MLOps Best Practices** - Experiment tracking, model registry, deployment
- **Data Analytics** - SQL, Python, real-time dashboards
- **Data Modeling & Quality** - dbt transformations, Great Expectations validation
- **LLM Applications** - RAG pipelines, vector databases, embeddings
- **Workflow Orchestration** - Airflow DAGs, quality gates, backfills
- **Cloud Architecture** - Scalable, production-ready patterns
- **DevOps** - Docker, CI/CD, containerization

## 🗂️ Project Structure

```
enterprise-ai-workflows/
├── project1-rapid-insights/        # Snowflake Cortex alternative
│   ├── app.py                      # Streamlit dashboard
│   ├── database.py                 # SQLite with AI functions
│   └── requirements.txt
│
├── project2-mlops-pipeline/        # Azure ML alternative
│   ├── docker-compose.yml          # MLflow + Jupyter + PostgreSQL
│   ├── notebooks/                  # Experiment notebooks
│   ├── models/                     # Model training scripts
│   └── deployment/                 # FastAPI deployment
│
├── project3-document-qa/           # LLM RAG application
│   ├── app.py                      # Gradio interface
│   ├── rag_pipeline.py             # Vector search + LLM
│   └── requirements.txt
│
├── data-platform/                  # Data modeling + analytics
│   ├── dbt/                        # dbt project (seeds, staging, marts)
│   ├── analytics_dashboard.py      # Streamlit BI dashboard
│   └── README.md
│
├── great_expectations/             # Data quality validation
│   ├── expectations/               # Expectation suites
│   ├── checkpoints/                # Validation checkpoints
│   └── README.md
│
├── airflow/                        # Optional orchestration layer
│   ├── dags/                       # DAG definitions
│   └── README.md
│
└── docs/                           # Additional documentation
    ├── setup-guide.md
    ├── interview-prep.md
    └── architecture-decisions.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- Docker Desktop (for Project 2)
- 5GB free disk space

### Installation

```bash
# Clone and enter the directory
cd enterprise-ai-workflows

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# Install dependencies for a specific project
cd project1-rapid-insights
pip install -r requirements.txt
```

### End-to-End (Data → Embeddings → RAG → Analytics)

```bash
# Build curated data (dbt transformations)
cd data-platform/dbt
dbt seed && dbt run && dbt test

# Refresh vector store from document_index mart
cd ../../
python scripts/refresh_embeddings.py --persist-dir project3-document-qa/chroma_store --reset

# Launch RAG application (consumes persistent Chroma store if present)
cd project3-document-qa
python app.py  # http://localhost:7860

# Launch analytics dashboard (BI view on marts)
cd ../data-platform
streamlit run analytics_dashboard.py  # http://localhost:8502
```

### One-Command Full Pipeline (dbt + Quality Gates + Embeddings)
Instead of running each step manually, you can execute the entire data & AI preparation workflow with a single script that:

1. Seeds and builds dbt models (staging + marts)
2. Runs all dbt tests (structural quality)
3. Performs semantic data quality checks (row count, schema, uniqueness, text length bounds)
4. Refreshes the Chroma vector store from the curated `document_index` mart
5. Verifies the vector store document count

Run from the repo root:
```bash
./scripts/run_full_pipeline.sh
```

Prerequisites (first time only):
```bash
pip install dbt-core dbt-duckdb great-expectations chromadb sentence-transformers streamlit
```

Sample output (abridged):
```
📥 STEP 1: dbt seed            ✅ Seeds loaded
🏗️  STEP 2: dbt run             ✅ 6 models built
🧪 STEP 3: dbt test            ✅ 18 tests passed
🔍 STEP 4: Quality Gate        ✅ All semantic checks passed
🧬 STEP 5: Refresh Embeddings  ✅ 21 embeddings stored
✔️  STEP 6: Verify Vector Store ✅ 21 documents
🎉 PIPELINE COMPLETE!
```

Artifacts produced:
- DuckDB warehouse: `data-platform/dbt/warehouse/data.duckdb`
- Persistent vector store: `project3-document-qa/chroma_store/`
- dbt docs site (build): `data-platform/dbt/target/index.html`

Use this script as an interview talking point for "end-to-end workflow orchestration with embedded quality gates" (even without Airflow).

Artifacts produced:
- DuckDB warehouse: `data-platform/dbt/warehouse/data.duckdb`
- Vector store: `project3-document-qa/chroma_store/` (persistent embeddings)
- Dashboard app: `data-platform/analytics_dashboard.py`

## 📊 Project Details

### Project 1: Rapid Insights Workflow
**Simulates:** Snowflake Cortex AI  
**Tech Stack:** Python, SQLite, Streamlit, TextBlob, NumPy  
**Features:**
- 📊 **Advanced Time Series Forecasting**: Intelligent trend detection with recent-window slope calculation and automatic seasonal pattern recognition
- 💬 **SQL-based Sentiment Analysis**: TextBlob integration via SQLite UDFs
- 📝 **Text Summarization**: Extractive summarization accessible through SQL
- 🧑‍💼 **HR & Payroll Analytics**: Sample datasets with payroll forecasting, employee tenure tracking, and overtime detection
- 🎨 **Interactive Dashboard**: Real-time visualizations with Plotly

**Run it:**
```bash
cd project1-rapid-insights
streamlit run app.py
```

**Live app:** https://enterprise-ai-workflows-d3ds3rasntycg5bwaqru5a.streamlit.app

**Key Innovations:**
- Momentum-based forecasting for trending data (captures recent patterns)
- Naive seasonal forecasting for cyclical data (repeats patterns intelligently)
- Smart cache management with version markers for seamless updates

### Project 2: Enterprise MLOps Pipeline
**Simulates:** Azure ML, Dataiku  
**Tech Stack:** MLflow, Docker, PostgreSQL, FastAPI, Scikit-learn  
**Features:**
- Experiment tracking
- Model registry
- Automated retraining
- REST API deployment
- CI/CD pipeline

**Run it:**
```bash
cd project2-mlops-pipeline
docker-compose up -d
# Access MLflow at http://localhost:5000
# Access Jupyter at http://localhost:8888
```

**Live deployments:**

Hugging Face Space (persistent demo):
- MLflow UI: https://zhangju2023-mlops-pipeline-demo.hf.space/mlflow/
- Model API: https://zhangju2023-mlops-pipeline-demo.hf.space/api/docs
 - Health: https://zhangju2023-mlops-pipeline-demo.hf.space/api/health
 - Example prediction: https://zhangju2023-mlops-pipeline-demo.hf.space/api/predict/example

 Notes:
 - Runs in demo mode by default (no external model required)
 - MLflow is auto-seeded with a demo model (customer_churn_model → Production)

GitHub Codespaces (temporary):
- MLflow UI: https://glorious-rotary-phone-g64w6j547wcwjpq-5000.app.github.dev
- Model API: https://glorious-rotary-phone-g64w6j547wcwjpq-8000.app.github.dev/docs
- Jupyter Notebook: https://glorious-rotary-phone-g64w6j547wcwjpq-8888.app.github.dev/lab/tree/notebooks/01_customer_churn_mlops.ipynb
  
  Note: Codespaces URLs are temporary and only reachable while that Codespace is running. After the Codespace auto-sleeps, click Resume in the Codespaces UI and restart services:    ```bash
    bash project2-mlops-pipeline/scripts/start-mlops-nodocker.sh
    ```
  
    If the Codespace is deleted, these URLs will no longer work; open a new Codespace from the quickstart link to spin up a fresh demo.

     Start/Resume the demo (opens a Codespace):
     https://codespaces.new/justin-mbca/enterprise-ai-workflows?quickstart=1
### Project 3: Document Q&A System

[![Open in Hugging Face Spaces](https://img.shields.io/badge/Spaces-Open%20App-blue?logo=huggingface)](https://huggingface.co/spaces/zhangju2023/document-qa-rag)

**Simulates:** Azure OpenAI RAG  
**Tech Stack:** ChromaDB, SentenceTransformers, Hugging Face Transformers  
**Features:**
- Document ingestion
- Vector embeddings
- Semantic search
- Question answering
- Web interface

**Run it:**
```bash
cd project3-document-qa
python app.py
# Access at http://localhost:7860
```

Live app: https://huggingface.co/spaces/zhangju2023/document-qa-rag

#### Integrated Data Platform Features
- Curated `document_index` mart (dbt) unifies HR, legal (arbitration & subrogation), and ML concept texts.
- Embedding refresh script (`scripts/refresh_embeddings.py`) builds a persistent Chroma store from dbt output.
- RAG app auto-detects persistent store and skips sample preload for production-like behavior.
- Analytics dashboard (`data-platform/analytics_dashboard.py`) visualizes mart KPIs (policy features, arbitration deadlines, document distribution).

#### Embedding Refresh Workflow
```bash
cd data-platform/dbt
dbt seed && dbt run
cd ../../
python scripts/refresh_embeddings.py --persist-dir project3-document-qa/chroma_store --reset
```
Then start the app:
```bash
cd project3-document-qa
export CHROMA_PERSIST_DIR="project3-document-qa/chroma_store"  # optional
python app.py
```

#### Analytics Dashboard
```bash
cd data-platform
streamlit run analytics_dashboard.py
```
Tabs: Overview, HR Policies, Arbitration Timelines, Document Index (export CSV/JSON).

## 💰 Cost Breakdown

| Component | Enterprise Tool | Free Alternative | Savings |
|-----------|----------------|------------------|---------|
| Data Warehouse | Snowflake ($2000+/year) | PostgreSQL + SQLite | $2000+ |
| MLOps Platform | Azure ML ($1000+/year) | MLflow + Docker | $1000+ |
| Low-code ML | Dataiku ($50k+/year) | Jupyter + Streamlit | $50k+ |
| LLM API | Azure OpenAI ($100+/month) | Open models (local) | $1200+ |
| Data Modeling | Commercial Data Platforms ($1000+) | dbt Core + DuckDB | $1000+ |
| **Total** | **$54,200+/year** | **$0** | **$54,200+** |

## 🎯 Interview Talking Points

### How to Discuss These Projects

**For Tool-Specific Questions:**
> "I implemented this using MLflow to master MLOps fundamentals—the concepts of experiment tracking, model versioning, and deployment pipelines transfer directly to Azure ML. I can adapt quickly to your tech stack."

**For Architecture Questions:**
> "I designed this to mirror production patterns: separate data layer, orchestration layer, and serving layer. Here's how I handled [specific challenge]..."

**For Problem-Solving Questions:**
> "When building my RAG pipeline, I optimized vector search performance by [specific solution]. This taught me [learning outcome]."

## 📚 Learning Path

### Week 1-2: Project 1 (Rapid Insights)
- Learn SQL-based analytics
- Implement AI functions
- Build interactive dashboards

### Week 3-4: Project 2 (MLOps)
- Set up experiment tracking
- Implement model lifecycle
- Deploy via REST API

### Week 5-6: Project 3 (Document Q&A)
- Work with embeddings
- Build vector search
- Create LLM application

### Week 7-8: Polish & Deploy
- Add CI/CD pipelines
- Write comprehensive docs
- Deploy to free hosting

## 🔗 Free Resources Used

- **Datasets:** Kaggle, UCI ML Repository
- **Models:** Hugging Face Hub
- **Hosting:** Streamlit Cloud, Railway.app, Render
- **Compute:** Google Colab, Kaggle Notebooks
- **Version Control:** GitHub (free tier)

## 🌟 Next Steps

### ✅ Phase 1 Reliability Foundations (Completed)
Phase 1 established baseline governance and transparency artifacts:

- `METRICS.md` – Canonical metric catalog with formulas + SLA targets.
- `DATA_SLA.md` – Schedule, quality gates, alerting & recovery procedures.
- `docs/data-lineage.md` – Mermaid lineage from seeds → staging → marts → quality gates → embeddings → serving.
- Enriched `data-platform/dbt/models/schema.yml` – Column-level descriptions + domain enumerations.

These artifacts position the project as an analytics engineering portfolio piece (showing modeling, documentation, observability, and reliability mindset).

### ✅ Phase 2 Self-Serve Analytics & Scalability (Completed)
Phase 2 introduced patterns for self-serve insights and data scalability:

- `data-platform/dbt/models/exposures.yml` – 4 exposures linking marts to downstream consumers (dashboards, RAG app, reports) with ownership metadata.
- `data-platform/dbt/models/sources.yml` – Source definitions with freshness configuration template (commented for seed-based sources; ready for production ingestion).
- `data-platform/dbt/models/marts/events_incremental.sql` – Incremental model demonstrating `is_incremental()` logic, unique key constraint, and timestamp-based filtering for scalability.
- Added schema docs for `events_incremental` model with 8 column definitions.

**Interview talking points:**
- Exposures = metrics observability + lineage to BI/apps (Anthropic values transparency).
- Incremental models = cost-efficient processing at scale (Anthropic handles massive data volumes).
- Source freshness = SLA enforcement (catches stale ingestion early).

Validated: dbt compile/run/test all pass (23 tests green, 7 models including 1 incremental).

### ✅ Phase 3 Reliability & Safety Monitoring (Completed)
Phase 3 adds interpretability and reliability features aligned with Anthropic's mission:

- `scripts/check_embedding_drift.py` – Detects distribution shifts in embedding L2 norms (mean ±10% threshold) vs historical baseline; exits non-zero to gate pipeline.
- `scripts/check_row_count_anomaly.py` – Z-score anomaly detection (threshold=3σ) on mart row counts using 7-day rolling window; flags unexpected spikes/drops.
- Updated `scripts/run_full_pipeline.sh` – Integrated Steps 5 (anomaly check) and 7 (drift check) with Slack failure detail via `--failures-file` flag.
- `.github/workflows/daily-validation.yml` – Scheduled daily workflow (06:00 UTC) running dbt tests + drift + anomaly checks; posts Slack summary; collects metrics snapshots as artifacts.
- Baseline files created: `metrics/baselines/embedding_norm.json`, `metrics/baselines/row_counts.json`.

**Why this matters (Anthropic alignment):**
- **Reliability:** Automated detection of data quality regressions and model drift before they reach production.
- **Interpretability:** Explicit baselines and statistical thresholds (Z-score, L2 norm) make decisions auditable.
- **Safety:** Drift detection acts as a kill switch—prevents deploying embeddings with unexpected distributions that could degrade RAG quality.

**Interview talking points:**
- Drift detection = model governance (catches encoder updates, input degradation).
- Anomaly detection = data SLA monitoring (row count stability ensures completeness).
- Daily validation workflow = proactive health checks (shift-left observability).
- Slack integration with `--failures-file` = actionable incident response (enumerate root causes).

Validated: drift/anomaly scripts run successfully; baselines initialized; pipeline integration tested.


1. **Start with Project 1** - Easiest to set up and run
2. **Document your learnings** - Keep notes on challenges and solutions
3. **Customize for your domain** - Use data relevant to your target industry
4. **Deploy publicly** - Show working demos in interviews
5. **Write blog posts** - Explain your implementation decisions

### 🔔 Alerts (CI + Data Quality)
This repo includes Slack alert integration at two layers:

- **CI Pipeline (GitHub Actions)**: `.github/workflows/full-pipeline.yml` posts a message on success or failure after running the end-to-end script.
- **Data Quality Gate (Semantic / GE)**: `scripts/run_full_pipeline.sh` sends a Slack alert if the semantic validation (Great Expectations + manual checks) fails before embedding refresh.

Setup:
1. Create an Incoming Webhook in your Slack workspace.
2. Add the webhook URL as a GitHub repository secret named `SLACK_WEBHOOK_URL` (Settings → Secrets and variables → Actions).
3. (Optional) For local testing, export the variable before running the script:
  ```bash
  export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXX/YYY/ZZZ"
  ./scripts/run_full_pipeline.sh
  ```

Alert script: `scripts/slack_notify.py` (emoji prefixes for success, failure, warning).
Extended alert script capabilities:

```bash
# Basic message (auto info emoji)
python3 scripts/slack_notify.py "Pipeline run complete"

# Explicit level
python3 scripts/slack_notify.py "dbt models built" --level success
python3 scripts/slack_notify.py "Quality gate failed" --level error

# Append failing expectations from a JSON or text file
python3 scripts/slack_notify.py "Quality gate failed" --level error --failures-file great_expectations/uncommitted/validations/latest.json

# Send a fully custom JSON payload (overrides other flags)
python3 scripts/slack_notify.py "placeholder" --raw-json payload.json

# Plain message without emoji
python3 scripts/slack_notify.py "Quiet notification" --no-emoji
```

Failure details file format examples handled by `--failures-file`:
- JSON list: `["row count mismatch","unexpected domain: finance"]`
- JSON object with `failures` key: `{ "failures": ["duplicate IDs", "text length spike"] }`
- Plain text file: one failure per line.

If the file has >15 lines it is truncated with a summary line.

Emoji got garbled? If you see characters like `ÿ...e2...9d...8c`, your terminal encoding or copy source mangled the UTF-8 emoji. Paste directly from a UTF-8 source or use ASCII text; the script inserts standard Slack emoji codes automatically for the `--level` values.

To extend alerts further (e.g., suppress success spam, include GE expectation statistics), add a step that writes a small JSON file of failures and pass its path via `--failures-file`.

### Data Platform & Quality Layer
This repo now includes **Great Expectations** for formal data quality validation:
- **Suite:** `great_expectations/expectations/document_index_suite.json` validates row counts, schema, domain values, text length bounds, and source lineage.
- **Checkpoint:** `great_expectations/checkpoints/document_index_checkpoint.yml` runs the suite against the `document_index` mart (DuckDB).
- **Airflow Integration:** `ge_document_index_validation` task gates embedding refresh—only proceeds if quality checks pass.
- **CI:** GitHub Actions workflow executes GE checkpoint before building vector store.

**Why it matters (interview framing):**
- Prevents semantic drift (e.g., unexpected domain "finance" stops embeddings).
- Demonstrates shift-left testing + SLA enforcement.
- Shows understanding of governance beyond structural dbt tests.

**Run GE checkpoint locally:**
```bash
cd great_expectations
REPO_ROOT=$(pwd)/.. great_expectations checkpoint run document_index_checkpoint
```

### Data Platform Next Steps (Optional)
- Add dbt metrics + semantic layer for standardized KPIs.
- Expand GE with statistical distribution checks (e.g., detect sudden text length shifts).
- Schedule embedding refresh via GitHub Actions to auto-sync RAG corpus.
- Add Lightdash/Evidence for richer BI exploration.

## 🛠 Optional: Airflow Orchestration Layer

If you want to demonstrate orchestration proficiency (e.g., for roles listing Airflow experience), this repo includes an optional Apache Airflow DAG that models a multi-step data & AI preparation pipeline.

**DAG:** `airflow/dags/data_platform_pipeline.py`

**Pipeline Steps:**
1. `dbt_seed` – Load seed CSVs into DuckDB
2. `dbt_run` – Build staging + marts (including `document_index`)
3. `dbt_test` – Enforce data quality (relationships, not_null, accepted_values)
4. `refresh_embeddings` – Rebuild persistent Chroma store from curated mart
5. `doc_vector_count_check` – Assert vector count matches document count

**Why It Matters (Interview Framing):**
- Shows canonical dataset construction & semantic enrichment.
- Demonstrates quality gates before downstream AI tasks.
- Illustrates daily scheduling & potential SLAs (05:00 UTC run window).
- Easy to extend with alerts, backfills, dynamic task mapping, and retraining branches.

**Quick Local Demo:**
```bash
export AIRFLOW_HOME="$(pwd)/airflow"
python -m venv venv && source venv/bin/activate
pip install -r airflow/requirements-airflow.txt
airflow db init
airflow variables set REPO_ROOT "$(pwd)"
airflow standalone  # UI at http://localhost:8080
```

**Backfill Example:**
```bash
airflow dags backfill data_platform_pipeline -s 2025-11-15 -e 2025-11-22
```

**Portfolio Note:** Airflow is optional—keeping GitHub Actions shows pragmatic minimalism, while the DAG demonstrates readiness for more complex orchestration when scale/SLAs require it.

**CI Showcase:** A GitHub Actions workflow (`.github/workflows/airflow-ci.yml`) installs Airflow and executes each DAG task via `airflow tasks test` (no scheduler needed) on push and a daily cron. Artifacts include the rendered DAG graph and the generated Chroma store.

## 🌐 Website

Static showcase (GitHub Pages): If Pages is enabled for this repo using the `/docs` folder, visit:
https://justin-mbca.github.io/enterprise-ai-workflows/

This site lists all projects and links to the live demos (Streamlit, Hugging Face Spaces, Codespaces).

## 🤝 Contributing

Have improvements or alternative implementations? PRs welcome!

## 📄 License

MIT License - Free to use for personal and commercial projects

## 💡 Additional Resources

- [Setup Guide](docs/setup-guide.md) - Detailed installation instructions
- [Interview Prep](docs/interview-prep.md) - Common questions and answers
- [Architecture Decisions](docs/architecture-decisions.md) - Why we chose each tool
- [Data Platform README](data-platform/README.md) - dbt & embedding integration details
- [Analytics Dashboard](data-platform/README_DASHBOARD.md) - BI layer usage

---

**Remember:** Companies hire problem-solvers, not tool experts. These projects prove you understand the underlying concepts and can build real solutions! 🚀

Built with ❤️ using 100% free and open-source tools.
