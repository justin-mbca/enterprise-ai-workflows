# Project 2 on Hugging Face Spaces (Docker)

Run the MLOps demo (MLflow UI + FastAPI API) on a single public URL using a Docker Space.

What this does
- Starts MLflow Tracking Server (SQLite backend, local artifacts)
- Starts the FastAPI model API
- Uses Nginx to expose both under one port with path routing:
  - /mlflow → MLflow UI
  - /api → FastAPI (OpenAPI at /api/docs)

Quick start (no GitHub Actions required)
1) Go to https://huggingface.co/spaces and create a new Space
   - Type: Docker
   - Name suggestion: `mlops-pipeline-demo`
   - Hardware: CPU Basic (free)
2) Upload the contents of this `hf-space/` folder:
   - `Dockerfile`
   - `nginx.conf.template`
   - `start.sh`
3) Save and let the Space build. First build can take a few minutes.
4) When it’s running, open:
   - MLflow UI: https://<your-space>/mlflow
   - API docs: https://<your-space>/api/docs

Notes
- Data is ephemeral on free Spaces. This is intended as a demo, not a persistent registry.
- If you trained and registered a model locally, you can rebuild with artifacts bundled, or point FastAPI to a public model artifact.
- If MLflow shows an Invalid Host header, the Nginx proxy here already sets `Host: localhost:5000` to satisfy MLflow 3.6.0 validation.

Optional: Link to GitHub for auto-updates
- You can link this Space to your GitHub repo and move these files to a separate Space-only repo, or keep Dockerfile-based clone (as in this setup).

Troubleshooting
- If /mlflow doesn’t load: wait for the app to be “Running” and refresh
- If /api/docs returns 503: train/register a model in MLflow and promote to Production first
- Check Space logs for Python errors and Nginx startup