---
title: Project 2 — MLOps Pipeline
---

# Project 2 — MLOps Pipeline (MLflow + FastAPI)

This project simulates an enterprise MLOps platform with experiment tracking, a model registry, and a deployment API.

## View the app

Live demo (Hugging Face Space):

<p>
  <a href="https://zhangju2023-mlops-pipeline-demo.hf.space/mlflow/">
    <img alt="MLflow UI" src="https://img.shields.io/badge/MLflow%20UI-0194E2">
  </a>
  <a href="https://zhangju2023-mlops-pipeline-demo.hf.space/api/docs">
    <img alt="API Docs" src="https://img.shields.io/badge/API%20Docs-009688?logo=fastapi&logoColor=white">
  </a>
  <a href="https://zhangju2023-mlops-pipeline-demo.hf.space/api/health">
    <img alt="Health" src="https://img.shields.io/badge/Health-4caf50">
  </a>
  <a href="https://zhangju2023-mlops-pipeline-demo.hf.space/api/predict/example">
    <img alt="Example" src="https://img.shields.io/badge/Example%20Prediction-7c4dff">
  </a>
</p>

One-click environment (GitHub Codespaces):
- https://codespaces.new/justin-mbca/enterprise-ai-workflows?quickstart=1

Deploy your own Hugging Face Space:
1. Create a new Space (Type: Docker, Hardware: CPU Basic)
2) Upload these files from the repo folder `project2-mlops-pipeline/hf-space/`:
   - Dockerfile
   - nginx.conf.template
   - seed_mlflow.py
   - start.sh
   - main_demo.py
3. Wait for the build to complete
4. Your Space will be at: https://<owner>-<space-name>.hf.space/mlflow/

Notes:
- Free Spaces are ephemeral; great for demos, not a persistent registry
- The Nginx proxy sets the Host header required by MLflow 3.6.0
- Demo Mode is enabled by default; API works without a trained model
- On startup, MLflow is auto-seeded with a demo model (customer_churn_model → Production)
- To load from the registry instead of demo predictions, set `DEMO_MODE=false` in Space Settings → Variables and rebuild

## Architecture

- MLflow Tracking Server (SQLite backend, local artifacts)
- FastAPI deployment API (serves predictions from the MLflow registry)
- Nginx reverse proxy routing /mlflow and /api over one port

## Repository

Code: https://github.com/justin-mbca/enterprise-ai-workflows/tree/main/project2-mlops-pipeline
