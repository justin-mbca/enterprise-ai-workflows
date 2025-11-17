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

## Troubleshooting (Recovery Mode / container error)

If you see “This codespace is currently running in recovery mode…”

1. View creation logs:
  - Cmd/Ctrl + Shift + P → “Codespaces: View Creation Log”
2. Rebuild container:
  - Cmd/Ctrl + Shift + P → “Codespaces: Rebuild Container”
3. Verify Docker is running inside the devcontainer:
  ```bash
  docker info
  docker compose version
  ```
  If not ready yet, retry for up to 2 minutes:
  ```bash
  for i in {1..60}; do docker info >/dev/null 2>&1 && echo "Docker ready" && break; sleep 2; done
  ```
4. If the error persists, ensure your devcontainer uses:
  - `ghcr.io/devcontainers/features/docker-in-docker:2` with `moby: true`
  - `overrideCommand: false`, `init: true`
  - Mount for `/var/lib/docker` as a volume

This repository’s `.devcontainer/devcontainer.json` is configured accordingly.
