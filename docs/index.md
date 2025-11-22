---
title: Enterprise AI Workflows
---

# Enterprise AI Workflows (Free + Open Source)

Showcase of three production-inspired projects you can run for free.

## Live demos

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
  <a href="https://huggingface.co/spaces/zhangju2023/document-qa-rag">
    <img alt="RAG App" src="https://img.shields.io/badge/Project%203-RAG%20App-ffcc4d?logo=huggingface&logoColor=black">
  </a>
</p>

## Projects

1. Rapid Insights (Streamlit)
   - Live demo: https://enterprise-ai-workflows-d3ds3rasntycg5bwaqru5a.streamlit.app
   - Code: https://github.com/justin-mbca/enterprise-ai-workflows/tree/main/project1-rapid-insights

2. MLOps Pipeline (MLflow + FastAPI)
   - Live demo (HF Space):
     - MLflow UI: https://zhangju2023-mlops-pipeline-demo.hf.space/mlflow/
     - API docs: https://zhangju2023-mlops-pipeline-demo.hf.space/api/docs
     - Health: https://zhangju2023-mlops-pipeline-demo.hf.space/api/health
   - One-click environment (Codespaces): https://codespaces.new/justin-mbca/enterprise-ai-workflows?quickstart=1
   - Code: https://github.com/justin-mbca/enterprise-ai-workflows/tree/main/project2-mlops-pipeline
   - Guide: /project2.html

3. Document Q&A (RAG on Gradio)
   - Live demo: https://huggingface.co/spaces/zhangju2023/document-qa-rag
   - Code: https://github.com/justin-mbca/enterprise-ai-workflows/tree/main/project3-document-qa

## Data & Pipeline Artifacts

- Daily Full Pipeline (dbt + quality + embeddings): See latest published summary
  - Summary Report: /pipeline/pipeline_report.html
  - Raw dbt Docs: /pipeline/dbt/index.html (lineage & model metadata)
  - Manifest & Catalog: /pipeline/dbt/manifest.json, /pipeline/dbt/catalog.json
  - Great Expectations Data Docs: /pipeline/ge/index.html

These pages auto-update via GitHub Actions after the full pipeline workflow runs (`full-pipeline.yml`).

## About

This site is a static showcase hosted on GitHub Pages. For Project 2, the running app is hosted on Hugging Face Spaces (Docker) or GitHub Codespaces; this site links to those live environments.

Source repo: https://github.com/justin-mbca/enterprise-ai-workflows
