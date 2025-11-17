#!/usr/bin/env bash
set -euo pipefail

# Start MLflow (SQLite backend) + Jupyter Lab + FastAPI API without Docker.
# Intended for constrained environments (e.g., Codespaces recovery mode).

cd "$(dirname "$0")/.."
WORKDIR=$(pwd)
LOGDIR="$WORKDIR/_nodocker_logs"
mkdir -p "$LOGDIR"

echo "Starting MLflow (SQLite backend) ..."
nohup mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root "$WORKDIR/mlruns" \
  > "$LOGDIR/mlflow.log" 2>&1 &

echo "Starting Jupyter Lab ..."
nohup jupyter lab \
  --ip=0.0.0.0 \
  --port=8888 \
  --NotebookApp.token='' \
  --NotebookApp.password='' \
  > "$LOGDIR/jupyter.log" 2>&1 &

echo "Starting FastAPI model API ..."
nohup uvicorn deployment.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  > "$LOGDIR/api.log" 2>&1 &

cat <<EOF
Services starting (logs in $LOGDIR):
- MLflow:   http://localhost:5000
- Jupyter:  http://localhost:8888
- API Docs: http://localhost:8000/docs

To tail logs:
  tail -f $LOGDIR/mlflow.log
  tail -f $LOGDIR/jupyter.log
  tail -f $LOGDIR/api.log

To stop all:
  pkill -f 'mlflow server' || true
  pkill -f 'jupyter-lab' || pkill -f 'jupyter lab' || true
  pkill -f 'uvicorn deployment.main:app' || true

EOF
