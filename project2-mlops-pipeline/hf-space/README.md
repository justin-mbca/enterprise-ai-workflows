# Project 2 on Hugging Face Spaces (Docker)

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

## Quick start (no GitHub Actions required)
1) Go to https://huggingface.co/spaces and create a new Space
   - Type: Docker
   - Name suggestion: `mlops-pipeline-demo`
   - Hardware: CPU Basic (free)
2) Upload the contents of this `hf-space/` folder:
   - `Dockerfile`
   - `nginx.conf.template`
   - `main_demo.py`
   - `start.sh`
   - `README.md`
3) Save and let the Space build. First build can take a few minutes.
4) When it's running, open:
   - **MLflow UI**: `https://<your-space>/mlflow/`
   - **API docs**: `https://<your-space>/api/docs`
   - **Health check**: `https://<your-space>/api/health`
   - **Test prediction**: `https://<your-space>/api/predict/example`

## Notes
- Data is ephemeral on free Spaces. This is intended as a demo, not a persistent registry.
- Demo mode uses rule-based predictions (no ML model required)
- If MLflow shows an Invalid Host header, the Nginx proxy sets `Host: localhost:5000` to satisfy MLflow 3.6.0 validation.

## Optional: Link to GitHub for auto-updates
- You can link this Space to your GitHub repo for automatic updates when you push changes

## Troubleshooting
- If /mlflow doesn't load: wait for the app to be "Running" and refresh
- If /api/docs returns 502: Check Space logs for Python/FastAPI errors
- Logs location: Space "Logs" tab or `/tmp/api.log` and `/tmp/mlflow.log`
