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

# Wait for upstream services to be ready before seeding/starting API and Nginx
echo "Waiting for MLflow TCP port 127.0.0.1:5000..."
for i in {1..60}; do
  if bash -c 'exec 3<>/dev/tcp/127.0.0.1/5000' 2>/dev/null; then
    exec 3>&- 3<&-
    echo "MLflow port is open."
    break
  fi
  sleep 1
done

# Give MLflow a few more seconds for the REST API to fully initialize
echo "Waiting for MLflow REST API to initialize..."
sleep 5

## Optionally seed MLflow with a demo model and promote to Production
echo "SEED_MLFLOW env var is: ${SEED_MLFLOW:-false}"
if [ "${SEED_MLFLOW:-false}" = "true" ]; then
  echo "Seeding MLflow with demo model..."
  python /app/repo/project2-mlops-pipeline/hf-space/seed_mlflow.py 2>&1 | tee /tmp/seed.log || echo "Seeding failed (non-fatal)"
  cat /tmp/seed.log
else
  echo "Skipping MLflow seeding (SEED_MLFLOW not set to true)"
fi

# Start FastAPI (demo mode - works without trained model)
cd /app/repo/project2-mlops-pipeline/hf-space
export DEMO_MODE=true
nohup python -m uvicorn main_demo:app \
  --host 0.0.0.0 \
  --port 8000 \
  --root-path /api \
  >/tmp/api.log 2>&1 &

echo "Waiting for FastAPI on 127.0.0.1:8000..."
for i in {1..60}; do
  if bash -c 'exec 3<>/dev/tcp/127.0.0.1/8000' 2>/dev/null; then
    exec 3>&- 3<&-
    echo "FastAPI is up."
    break
  fi
  sleep 1
done

# Start Nginx in foreground
nginx -g 'daemon off;'
