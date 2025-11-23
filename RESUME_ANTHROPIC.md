# Xiangli Zhang · Grand Forks, ND · U.S. Permanent Resident
📧 justinzhang.xl@gmail.com | 📱 505-709-8187  
🔗 LinkedIn: [linkedin.com/in/justinzh/](https://linkedin.com/in/justinzh/) | GitHub: [github.com/justin-mbca](https://github.com/justin-mbca)

---

## SUMMARY

Staff Data Scientist with 15+ years' experience building **reliable, interpretable AI/ML systems** across healthcare, enterprise analytics, and data platforms. Expert in **data quality governance**, **drift detection**, **anomaly monitoring**, and **production pipelines** using Python, dbt, SQL, and cloud infrastructure. Proven track record delivering **self-serve analytics platforms**, **semantic data modeling**, and **safety-first ML systems** that enable data-driven decision-making while prioritizing reliability and interpretability.

---

## EDUCATION & CERTIFICATIONS

**MicroMasters, Statistics & Data Science** – MIT  
**IBM Data Science Professional Certificate**  
**B.Sc., Bioinformatics** – Simon Fraser University  
**B.Eng., Chemical Engineering** – Tsinghua University

---

## PROJECTS & PORTFOLIO

### Enterprise AI Workflows — Production Data Platform & ML/AI Portfolio (10/2025–Present)
**GitHub:** [github.com/justin-mbca/enterprise-ai-workflows](https://github.com/justin-mbca/enterprise-ai-workflows)

**Data Platform & Reliability Engineering:**
- **Semantic Data Modeling:** Built dbt-powered transformation layer (7 models, 23 tests) with staging → marts → serving architecture; created **METRICS.md catalog** defining 12 canonical metrics with grain/SLA/ownership → established single source of truth for analytics consumers
- **Data Quality Governance:** Implemented **Great Expectations validation suites** + **anomaly detection (Z-score monitoring)** on mart row counts; designed **DATA_SLA.md** defining freshness targets, quality gates, alerting pathways, and escalation procedures → ensured reliable data delivery
- **Drift Detection & Safety:** Developed **embedding drift monitoring** using L2 norm distribution checks (±10% threshold) as **blocking pipeline gate**; created proactive **daily validation workflow (GitHub Actions)** running dbt tests + drift/anomaly checks → caught data quality issues before production impact
- **Self-Serve Analytics:** Built **dbt exposures** linking 4 marts to downstream consumers (dashboards, RAG apps, reports); designed **incremental models** for scalability; created **Streamlit analytics dashboard** for KPI monitoring and corpus exploration → enabled stakeholder self-service

**MLOps & Production AI:**
- **MLOps Platform:** Automated retraining, CI/CD, **MLflow + FastAPI deployment** → achieved 99% uptime, <200ms latency, and $300K+ projected cost savings
- **Document Intelligence (RAG):** Built **HuggingFace + ChromaDB** vector pipeline with persistent storage; integrated dbt `document_index` mart → RAG application via **refresh_embeddings.py script** → enabled semantic search and compliance Q&A
- **Predictive Analytics:** Time-series forecasting, sentiment scoring, SQL feature pipelines → improved workforce planning and data-driven decision-making

**Infrastructure & Orchestration:**
- **Cloud Architecture:** Dockerized services on AWS-equivalent cloud; PostgreSQL + DuckDB + object storage + autoscaling → ensured robust, production-grade AI infrastructure
- **Pipeline Orchestration:** Airflow DAGs with quality gates, backfills, and monitoring; integrated Slack alerting for failures and drift detection → maintained operational awareness

**Key Technical Decisions Aligned with Anthropic Values:**
- **Interpretability:** Drift detection reveals when model behavior changes; data lineage diagrams (Mermaid) trace data flow from source → serving
- **Reliability:** Statistical monitoring (Z-score anomalies, L2 norm drift) with blocking gates prevents bad data propagation
- **Self-Serve Enablement:** dbt exposures + semantic layer + dashboard empower stakeholders to answer own questions safely

---

## AI COMPETITIONS & AWARDS

**2025** — Team Lead: **Cardiovascular AI Pre-Screening Tool** (LLMs + Gradio) → improved early-detection accuracy by 22%  
**2024** — Honorable Mention: **Personal Health Concierge Chatbot** (AWS SageMaker + Bedrock, Python, GenAI, AWS, NLP, AI/ML, LLM) → 92% semantic retrieval accuracy  
**2023** — Innovation Award: **Diabetes Recommendation Engine** (GPT + LangChain + Pinecone) → 30% improvement in recommendation relevance

---

## PROFESSIONAL EXPERIENCE

### McKesson – Data Engineer | Allen, TX | 08/2023 – 08/2025

- Built **ETL pipelines** for genomic variant data (100K+ oncology patients) → improved reliability and **reduced processing time by 40%**
- Designed **Python + SQL data quality validation** framework → prevented clinical reporting errors and ensured governance compliance
- Automated transformation logic for clinician dashboards → **increased data coverage by 35%** and enabled self-serve analytics
- Collaborated with scientists & engineers → ensured pipelines supported data-driven clinical decisions with reliable, interpretable outputs

### Freelance Data Scientist | Remote | 05/2023 – 08/2023

- Delivered **KNN recommendation & Random Forest forecasting models** → improved revenue planning by 15–20%
- Built **Python GUI** for RNA-Seq alignment & dashboards → reduced analysis time by 60%

### Daiichi Sankyo – Bioinformatics / ML Developer | Basking Ridge, NJ | 10/2019 – 02/2023

- Developed **ML-based variant annotation & biomarker discovery** → reduced analysis turnaround by 30–50%
- Created **reproducible RNA-seq/NGS pipelines** → streamlined multi-omics workflows and ensured data quality
- Supported predictive modeling → improved experimental prioritization with interpretable feature engineering

### Los Alamos National Laboratory – Computational Biology Researcher | 10/2017 – 10/2019

- Designed **ML pipelines** for large-scale sequence analysis → increased throughput by 40%
- Optimized **HPC workflows** → improved runtime and reproducibility for federal genomic projects
- Delivered insights for biodefense & pathogen analytics → enabled actionable scientific decisions

### UT Southwestern Medical Center – Bioinformatics Engineer | Dallas, TX | 2015 – 2018

- Built **mutation-calling & cancer-subtyping algorithms** → accelerated research throughput by 25%
- Developed **reusable data engineering workflows** → improved team productivity
- Co-authored peer-reviewed publications → increased scientific impact

---

## TECHNICAL SKILLS

**Languages:** Python, R, SQL, SAS, Perl, C/C++, Shell, VB.NET  
**Data Engineering:** dbt Core, DuckDB, PostgreSQL, Snowflake, Databricks, Spark, Apache NiFi, ETL/ELT pipelines  
**Data Quality & Monitoring:** Great Expectations, Z-score anomaly detection, drift detection, statistical validation  
**ML/AI:** NLP, LLMs, Transformers, predictive modeling, deep learning, interpretability techniques  
**Frameworks/Tools:** MLflow, Docker, FastAPI, HuggingFace, LangChain, ChromaDB, SentenceTransformers  
**Cloud:** AWS, Azure ML, GCP; Orchestration: Airflow, GitHub Actions, CI/CD  
**Visualization:** Power BI, Tableau, Streamlit, R Shiny, Plotly  
**Analytics:** Semantic modeling, self-serve platforms, metric governance, exposure management

---

## KEY ACCOMPLISHMENTS

✅ **Reliability-First Mindset:** Built drift detection and anomaly monitoring systems preventing bad data from reaching production  
✅ **Self-Serve Analytics:** Enabled stakeholders with dbt semantic layer, exposures, and interactive dashboards  
✅ **Data Governance:** Created METRICS.md catalog + DATA_SLA.md framework establishing single source of truth  
✅ **Production Impact:** $300K+ cost savings via MLOps automation; 40% pipeline efficiency gains; 99% uptime  
✅ **Interpretability Focus:** Data lineage diagrams, statistical monitoring, and transparent transformation logic

---

*Portfolio demonstrates Anthropic-aligned values: interpretability, reliability, safety-minded engineering, and enabling others through self-serve platforms.*
