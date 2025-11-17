#!/usr/bin/env bash
set -euo pipefail

# Expand nginx template with PORT env (fallback if envsubst is missing)
if command -v envsubst >/dev/null 2>&1; then
  envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
else
  # Simple fallback using sed
  sed "s/\${PORT}/${PORT}/g" /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
fi

# Paths
APP_ROOT="/app/repo/project2-mlops-pipeline"

# Start MLflow tracking server (SQLite + local artifacts)
export MLFLOW_TRACKING_URI="http://127.0.0.1:5000"
mkdir -p /data/artifacts
nohup mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri "$MLFLOW_BACKEND_URI" \
  --default-artifact-root "$MLFLOW_ARTIFACT_ROOT" \
  >/tmp/mlflow.log 2>&1 &

# Start FastAPI (points to local MLflow)
cd /app/repo/project2-mlops-pipeline/deployment
nohup python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  >/tmp/api.log 2>&1 &

# Start Nginx in foreground
nginx -g 'daemon off;'
