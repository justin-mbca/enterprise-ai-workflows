# Project 2: Run in GitHub Codespaces (Free-tier friendly)

This guide shows how to run the MLOps stack in GitHub Codespaces. If Docker Compose fails (recovery mode), use the no-Docker fallback script.

## Quickstart

1. Open this repo in Codespaces:
   - Badge: https://codespaces.new/justin-mbca/enterprise-ai-workflows?quickstart=1
   - Or GitHub UI → Code → Create codespace on `main`

2. Wait for the dev container to build (~1–3 minutes). It includes Docker-in-Docker.

3. If Docker is healthy:
```bash
cd project2-mlops-pipeline
docker compose up -d
```
Make ports public: 5000, 5001, 8000, 8888

4. If you are in recovery mode / Docker errors, use fallback (no Docker, SQLite backend):
```bash
bash project2-mlops-pipeline/scripts/start-mlops-nodocker.sh
```

5. Open the forwarded URLs:
- MLflow: port 5000
- (No proxy needed in fallback)
- Jupyter: port 8888
- API docs: port 8000

Notes:
- Ports may need manual Public toggle in the Ports panel.
- Docker mode: fix artifact perms if needed:
  ```bash
  docker exec mlops-jupyter chown -R jovyan:users /mlflow
  ```
- Fallback mode: artifacts stored locally under `mlruns/` (no permission tweak required).
- Keep training light; Codespaces has limited CPU/RAM.

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
4. If the error persists, switch to fallback permanently (current devcontainer now uses Python image without Docker feature). Skip Compose and use the script:
```bash
bash project2-mlops-pipeline/scripts/start-mlops-nodocker.sh
```
