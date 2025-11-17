---
title: MLOps Pipeline Demo
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

# Project 2: MLOps Model Deployment Pipeline

Run the MLOps demo (MLflow UI + FastAPI API) on a single public URL using a Docker Space.

## 🎭 Demo Mode

This Space runs in **demo mode** by default - the FastAPI works WITHOUT requiring pre-trained models:
- ✅ MLflow tracking server is fully functional for viewing experiments
- ✅ FastAPI endpoints return simulated predictions for testing
- ✅ All API endpoints respond correctly (health, predict, batch predict)
- ✅ Perfect for showcasing the MLOps architecture

**To use real models**: Train and register a model in MLflow, set `DEMO_MODE=false`, restart Space.

## What this does
- Starts MLflow Tracking Server (SQLite backend, local artifacts)
- Starts the FastAPI model API (with demo predictions)
- Uses Nginx to expose both under one port with path routing:
  - `/mlflow` → MLflow UI
  - `/api` → FastAPI (OpenAPI at /api/docs)

## Access Points

When the Space is running, try these endpoints:
- **MLflow UI**: `/mlflow/` - View experiments and models
- **API docs**: `/api/docs` - Interactive FastAPI documentation
- **Health check**: `/api/health` - Service status
- **Test prediction**: `/api/predict/example` - Try a sample prediction

## Architecture

```
User Request
    ↓
Nginx (port 7860)
    ├─→ /mlflow/ → MLflow Server (port 5000)
    └─→ /api/    → FastAPI (port 8000, demo mode)
```

## Notes
- Data is ephemeral on free Spaces. This is intended as a demo, not a persistent registry.
- Demo mode uses rule-based predictions (no ML model required)
- If MLflow shows an Invalid Host header, the Nginx proxy sets `Host: localhost:5000` to satisfy MLflow 3.6.0 validation.

## Source Code

Full source code and local setup instructions: [enterprise-ai-workflows](https://github.com/justin-mbca/enterprise-ai-workflows/tree/main/project2-mlops-pipeline)

## Troubleshooting
- If /mlflow doesn't load: wait for the app to be "Running" and refresh
- If /api/docs returns 502: Check Space logs for Python/FastAPI errors
- Logs location: Space "Logs" tab or `/tmp/api.log` and `/tmp/mlflow.log`
