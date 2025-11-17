---
title: Project 2 — MLOps Pipeline
---

# Project 2 — MLOps Pipeline (MLflow + FastAPI)

This project simulates an enterprise MLOps platform with experiment tracking, a model registry, and a deployment API.

## View the app

- One-click environment (Codespaces):
  https://codespaces.new/justin-mbca/enterprise-ai-workflows?quickstart=1

- Deploy on Hugging Face Spaces (single public URL):
  1. Create a new Space (Type: Docker, Hardware: CPU Basic)
  2. Upload these files from the repo folder `project2-mlops-pipeline/hf-space/`:
     - Dockerfile
     - nginx.conf.template
     - start.sh
  3. Wait for the build to complete
  4. Open:
     - MLflow UI → https://<your-space>/mlflow
     - API docs → https://<your-space>/api/docs

Notes:
- Free Spaces are ephemeral; great for demos, not a persistent registry
- The Nginx proxy sets the Host header required by MLflow 3.6.0

## Architecture

- MLflow Tracking Server (SQLite backend, local artifacts)
- FastAPI deployment API (serves predictions from the MLflow registry)
- Nginx reverse proxy routing /mlflow and /api over one port

## Repository

Code: https://github.com/justin-mbca/enterprise-ai-workflows/tree/main/project2-mlops-pipeline
