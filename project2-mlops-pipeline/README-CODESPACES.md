# Project 2: Run in GitHub Codespaces (Free-tier friendly)

This guide shows how to run the full MLOps stack (Docker Compose) in GitHub Codespaces using a Dev Container that includes Docker-in-Docker.

## Quickstart

1. Open this repo in Codespaces:
   - Badge: https://codespaces.new/justin-mbca/enterprise-ai-workflows?quickstart=1
   - Or GitHub UI → Code → Create codespace on `main`

2. Wait for the dev container to build (~1–3 minutes). It includes Docker-in-Docker.

3. Start the stack:

```bash
cd project2-mlops-pipeline
docker compose up -d
```

4. Make ports public (if prompted or via Ports panel): 5000, 5001, 8000, 8888

5. Open the forwarded URLs:
- MLflow: MLflow (port 5000)
- Proxy: MLflow Proxy (port 5001)
- Jupyter: Jupyter (port 8888)
- API docs: Model API (port 8000)

Notes:
- The devcontainer exposes ports as public by default, but you may still need to confirm in the Ports panel.
- If artifacts fail to log from Jupyter, ensure `/mlflow` is writable by the `jovyan` user:
  ```bash
  docker exec mlops-jupyter chown -R jovyan:users /mlflow
  ```
- Codespaces resources are limited; this stack is light but avoid heavy training jobs.

## Cleanup

```bash
docker compose down -v
```

Then stop/delete the Codespace from the GitHub UI.
