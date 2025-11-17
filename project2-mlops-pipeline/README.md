# Project 2: MLOps Pipeline with Docker

This project demonstrates a complete MLOps pipeline using:
- **MLflow** - Experiment tracking and model registry
- **Jupyter Lab** - Interactive development
- **PostgreSQL** - Metadata storage
- **FastAPI** - Model serving API

## Quick Start

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Cloud Deployment (VM)

Want to run this stack on a cloud VM (Azure/AWS/GCP) with a single command? See the Cloud Guide:

- Cloud guide: ./README-CLOUD.md

This includes a one-liner to install Docker, clone this repo, open firewall ports, and start the stack.

## Run Online (GitHub Codespaces)

[Open in Codespaces](https://codespaces.new/justin-mbca/enterprise-ai-workflows?quickstart=1)

Then:

```bash
cd project2-mlops-pipeline
docker compose up -d
```

Make ports 5000, 5001, 8000, 8888 public in the Ports panel. See details in `README-CODESPACES.md`.

## Accessing Services

- **MLflow UI**: http://localhost:5000
- **MLflow Proxy**: http://localhost:5001 (for internal Docker communication)
- **Jupyter Lab**: http://localhost:8888 (no password)
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

## Using the Platform

### 1. Train Models in Jupyter

1. Open http://localhost:8888
2. Navigate to `work/` folder
3. Open `01_customer_churn_mlops.ipynb`
4. Run all cells to train models

### 2. View Experiments in MLflow

1. Open http://localhost:5000
2. Click on "customer-churn-prediction" experiment
3. Compare different model runs
4. View metrics and artifacts

### 3. Test the Model API

#### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Make prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "tenure": 12,
      "monthly_charges": 70.50,
      "total_charges": 846.00,
      "contract_type": "Month-to-month",
      "payment_method": "Electronic check",
      "internet_service": "Fiber optic",
      "online_security": "No",
      "tech_support": "No"
    }
  }'
```

#### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={
        "features": {
            "tenure": 12,
            "monthly_charges": 70.50,
            "total_charges": 846.00,
            "contract_type": "Month-to-month",
            "payment_method": "Electronic check",
            "internet_service": "Fiber optic",
            "online_security": "No",
            "tech_support": "No"
        }
    }
)

print(response.json())
```

#### Using Interactive Docs

Visit http://localhost:8000/docs for interactive API testing

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MLOps Platform                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐              │
│  │   Jupyter    │─────▶│ MLflow Proxy │              │
│  │   Lab        │      │   (nginx)    │              │
│  │              │      └──────┬───────┘              │
│  └──────────────┘             │                       │
│         │                     ▼                       │
│         │              ┌──────────────┐              │
│         │              │   MLflow     │              │
│         │              │   Tracking   │              │
│         │              │   Server     │              │
│         │              └──────┬───────┘              │
│         │                     │                       │
│         │                     ▼                       │
│         │              ┌──────────────┐              │
│         │              │ PostgreSQL   │              │
│         │              │ (Metadata)   │              │
│         │              └──────────────┘              │
│         │                                             │
│         ▼                                             │
│  ┌──────────────┐      ┌──────────────┐              │
│  │   Model      │─────▶│   FastAPI    │              │
│  │   Registry   │      │   Server     │              │
│  └──────────────┘      └──────────────┘              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
project2-mlops-pipeline/
├── docker-compose.yml          # Service orchestration
├── deployment/
│   ├── Dockerfile             # API container
│   ├── main.py                # FastAPI application
│   └── requirements.txt       # API dependencies
├── notebooks/
│   └── 01_customer_churn_mlops.ipynb  # Training notebook
├── models/                    # Model artifacts (created at runtime)
└── data/                      # Data files (created at runtime)
```

## Service Details

### MLflow Tracking Server

- **Port**: 5000
- **Version**: 3.6.0 (with Host header validation)
- **Backend Store**: PostgreSQL
- **Artifact Store**: Local filesystem (`/mlflow/artifacts`)
- **Purpose**: Track experiments, log metrics, store models

### MLflow Proxy

- **Port**: 5001 (external), 80 (internal)
- **Technology**: Nginx (Alpine)
- **Purpose**: Proxy requests from Jupyter to MLflow with correct Host header
- **Configuration**: `mlflow/nginx.conf`

### Jupyter Lab

- **Port**: 8888
- **Image**: jupyter/datascience-notebook
- **User**: `jovyan` (UID 1000) via sudo from root
- **Purpose**: Interactive model development
- **Environment**: 
  - `MLFLOW_TRACKING_URI=http://mlflow-proxy`
  - `NB_UID=1000`, `NB_GID=100`
  - `GRANT_SUDO=yes`
- **Volumes**:
  - `notebooks/` → `/home/jovyan/work`
  - `models/` → `/home/jovyan/models`
  - `data/` → `/home/jovyan/data`
  - `mlflow_artifacts` → `/mlflow/artifacts` (shared with MLflow)

### PostgreSQL

- **Port**: 5432
- **Database**: mlops_db
- **User**: mlops_user
- **Purpose**: Store MLflow metadata
- **Persistence**: Docker volume

### FastAPI Model Server

- **Port**: 8000
- **Purpose**: Serve model predictions
- **Features**:
  - Automatic model loading from registry
  - Health checks
  - Batch predictions
  - Model info endpoint
  - Hot reload capability

## Common Operations

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f mlflow
docker-compose logs -f jupyter
docker-compose logs -f model-api
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart mlflow
```

### Stop Services

```bash
# Stop but keep data
docker-compose down

# Stop and remove data volumes
docker-compose down -v
```

### Access Service Shell

```bash
# Jupyter container
docker-compose exec jupyter bash

# MLflow container
docker-compose exec mlflow sh

# PostgreSQL
docker-compose exec postgres psql -U mlops_user -d mlops_db
```

### Update Services

```bash
# Pull latest images
docker-compose pull

# Rebuild containers
docker-compose build

# Restart with new images
docker-compose up -d
```

## Troubleshooting

### MLflow 3.6.0 Host Header Validation

**Issue**: MLflow 3.6.0 has strict Host header validation that rejects requests from Docker containers with "403 Invalid Host header - possible DNS rebinding attack detected"

**Solution**: We use an nginx reverse proxy (`mlflow-proxy`) that:
- Forwards requests from Jupyter to MLflow
- Sets the correct `Host: localhost:5000` header
- Satisfies MLflow's security middleware

**Configuration**:
- Jupyter uses `MLFLOW_TRACKING_URI=http://mlflow-proxy`
- Proxy listens on port 5001 (exposed) and port 80 (internal)
- MLflow only accepts requests with `Host: localhost:5000` header

### Artifact Write Permissions

**Issue**: PermissionError when logging model artifacts

**Solution**: 
```bash
# Fix ownership of /mlflow directory
docker exec mlops-jupyter chown -R jovyan:users /mlflow
```

The Jupyter kernel runs as `jovyan` user (not root), so the artifact directory must be writable by this user.

### Port Already in Use

```bash
# Check what's using the port
lsof -i :5000  # MLflow
lsof -i :8888  # Jupyter
lsof -i :8000  # API

# Kill the process or change ports in docker-compose.yml
```

### API Can't Load Model

**Issue**: "Model not found" error

**Solution**:
1. Make sure you've run the Jupyter notebook to train and register a model
2. Check MLflow UI to verify model is in "Production" stage
3. Check API logs: `docker-compose logs model-api`

### MLflow UI Shows No Experiments

**Solution**:
1. Open Jupyter notebook
2. Run cells to create and log experiments
3. Refresh MLflow UI

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Out of Memory

**Solution**:
1. Increase Docker memory in Docker Desktop
   - Preferences → Resources → Memory → 4GB or more
2. Reduce dataset size in notebooks
3. Use smaller models

### Services Won't Start

```bash
# Clean up everything
docker-compose down -v

# Remove orphaned containers
docker-compose down --remove-orphans

# Start fresh
docker-compose up -d
```

## MLflow Model Registry Workflow

### 1. Register Model

```python
# In Jupyter notebook
import mlflow

# Log model during training
with mlflow.start_run():
    mlflow.sklearn.log_model(model, "model")
    run_id = mlflow.active_run().info.run_id

# Register to registry
model_uri = f"runs:/{run_id}/model"
mlflow.register_model(model_uri, "customer_churn_model")
```

### 2. Transition Model Stage

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Promote to Production
client.transition_model_version_stage(
    name="customer_churn_model",
    version=1,
    stage="Production"
)
```

### 3. Load Model in API

```python
import mlflow

# API automatically loads Production model
model = mlflow.pyfunc.load_model("models:/customer_churn_model/Production")
```

## Performance Tuning

### For Development

- Reduce dataset size
- Use fewer model iterations
- Skip hyperparameter tuning

### For Production

- Scale horizontally (multiple API instances)
- Add load balancer (nginx)
- Use model caching
- Enable async predictions
- Add monitoring (Prometheus)

## Next Steps

1. **Customize Models**
   - Try different algorithms
   - Tune hyperparameters
   - Add feature engineering

2. **Add CI/CD**
   - GitHub Actions for testing
   - Automated model deployment
   - Integration tests

3. **Deploy to Cloud**
   - Kubernetes for orchestration
   - Managed MLflow (Databricks)
   - Cloud storage for artifacts

4. **Add Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alert system

## Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

**Built with ❤️ for learning MLOps**
