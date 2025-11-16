# MLOps Pipeline Setup Notes

## Session Summary - November 16, 2025

### Problem We Solved

Successfully configured MLflow 3.6.0 with Jupyter Lab in Docker, overcoming two major issues:

1. **MLflow Host Header Validation** - MLflow 3.6.0 introduced strict Host header security that blocks requests from Docker containers
2. **Artifact Write Permissions** - Jupyter kernel running as `jovyan` user couldn't write to root-owned artifact directory

---

## Solution Architecture

### 1. MLflow Proxy (Nginx)

**Problem**: MLflow 3.6.0 rejects requests with `Host: mlflow-proxy` or `Host: mlflow:5000`, responding with:
```
403 Forbidden
Invalid Host header - possible DNS rebinding attack detected
```

**Solution**: Nginx reverse proxy that rewrites the Host header

**Implementation**:
```nginx
# mlflow/nginx.conf
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://mlflow:5000;
        proxy_set_header Host "localhost:5000";  # ← Key line!
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Docker Compose**:
```yaml
mlflow-proxy:
  image: nginx:alpine
  container_name: mlops-mlflow-proxy
  ports:
    - "5001:80"
  volumes:
    - ./mlflow/nginx.conf:/etc/nginx/conf.d/default.conf:ro
  depends_on:
    - mlflow
  networks:
    - mlops-network
```

**Result**: 
- Jupyter connects to `http://mlflow-proxy`
- Proxy forwards to `http://mlflow:5000` with `Host: localhost:5000`
- MLflow accepts the request ✅

---

### 2. Artifact Write Permissions

**Problem**: 
```python
PermissionError: [Errno 13] Permission denied: '/mlflow/artifacts/1'
```

**Root Cause**:
- Jupyter datascience-notebook runs as root via Docker
- But uses `sudo` to execute Jupyter Lab as `jovyan` user (UID 1000)
- Notebook kernel inherits `jovyan` user context
- Volume `/mlflow/artifacts` mounted as `root:root` with `drwxr-xr-x` (755)
- `jovyan` can read but **cannot write**

**Process Tree**:
```
root (Docker)
└─ sudo --user jovyan jupyter lab
   └─ jovyan (Jupyter server)
      └─ jovyan (notebook kernel) ← This process needs write access!
```

**Solution**:
```bash
# Fix ownership to match Jupyter kernel user
docker exec mlops-jupyter chown -R jovyan:users /mlflow
```

**Docker Compose Configuration**:
```yaml
jupyter:
  user: root                           # Container runs as root
  environment:
    - MLFLOW_TRACKING_URI=http://mlflow-proxy
    - NB_UID=1000                       # jovyan user UID
    - NB_GID=100                        # users group GID
    - GRANT_SUDO=yes                    # Allow sudo
    - CHOWN_HOME=yes                    # Fix home directory ownership
  volumes:
    - mlflow_artifacts:/mlflow/artifacts  # Shared artifact storage
```

**Result**:
- `/mlflow` owned by `jovyan:users`
- Kernel can create experiment directories
- Model artifacts log successfully ✅

---

### 3. Package Dependencies

**Problem**: Conflicting dependency requirements
```
mlflow 3.6.0 requires cryptography>=43.0.0,<47
pyopenssl 23.2.0 requires cryptography>=38.0.0,<42
```
These ranges don't overlap! ❌

**Failed Approach**:
```python
# This causes conflicts
%pip install -q "cryptography>=38.0.0,<42" "pyopenssl>=23.2.0"
%pip install -q "mlflow==3.6.0"
```

**Working Solution**:
```python
# Let MLflow install its own dependencies first
%pip install -q --upgrade pip
%pip uninstall -y -q streamlit pyopenssl cryptography || true
%pip install -q "mlflow==3.6.0"  # Installs compatible deps
%pip install -q scikit-learn pandas numpy matplotlib seaborn
```

**Result**: No dependency conflicts ✅

---

## Configuration Files Changed

### 1. `docker-compose.yml`

**Added MLflow Proxy**:
```yaml
mlflow-proxy:
  image: nginx:alpine
  container_name: mlops-mlflow-proxy
  ports:
    - "5001:80"
  volumes:
    - ./mlflow/nginx.conf:/etc/nginx/conf.d/default.conf:ro
  depends_on:
    - mlflow
  networks:
    - mlops-network
```

**Updated Jupyter Service**:
```yaml
jupyter:
  user: root
  environment:
    - MLFLOW_TRACKING_URI=http://mlflow-proxy  # ← Use proxy
    - NB_UID=1000
    - NB_GID=100
    - GRANT_SUDO=yes
    - CHOWN_HOME=yes
  volumes:
    - ./notebooks:/home/jovyan/work
    - ./models:/home/jovyan/models
    - ./data:/home/jovyan/data
    - mlflow_artifacts:/mlflow/artifacts      # ← Shared volume
  depends_on:
    - mlflow
    - mlflow-proxy                            # ← New dependency
```

### 2. `mlflow/nginx.conf` (NEW)

Created nginx configuration to proxy requests with correct Host header.

### 3. `notebooks/01_customer_churn_mlops.ipynb`

**Cell 1 (NEW)**: Force-set tracking URI
```python
import os
os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow-proxy"
print(f"✅ Set MLFLOW_TRACKING_URI to: {os.environ['MLFLOW_TRACKING_URI']}")
```

**Cell 2**: Simplified package installation
```python
%pip install -q --upgrade pip
%pip uninstall -y -q streamlit pyopenssl cryptography || true
%pip install -q "mlflow==3.6.0"
%pip install -q scikit-learn pandas numpy matplotlib seaborn
print("✅ Package installation complete")
```

**Cell 5**: Updated MLflow setup to check environment variable first

### 4. `README.md`

- Added MLflow Proxy to architecture diagram
- Added troubleshooting section for Host header validation
- Added troubleshooting section for artifact permissions
- Updated service documentation with proxy details
- Added Jupyter environment variable documentation

---

## Testing & Verification

### 1. Verify Proxy Works

```bash
# From Jupyter container
docker exec mlops-jupyter curl -I http://mlflow-proxy/

# Expected: HTTP 200 OK
```

### 2. Verify Artifact Permissions

```bash
# Check ownership
docker exec mlops-jupyter ls -la /mlflow/

# Expected:
# drwxr-xr-x 3 jovyan users 4096 /mlflow/artifacts
```

### 3. Verify MLflow Connection

```python
# In Jupyter notebook
import mlflow
mlflow.set_tracking_uri("http://mlflow-proxy")
print(mlflow.get_tracking_uri())

# Expected: http://mlflow-proxy
```

### 4. Test Model Logging

```python
# Should complete without PermissionError
with mlflow.start_run():
    mlflow.log_param("test", "value")
    mlflow.sklearn.log_model(model, "model")
```

---

## Key Learnings

### 1. MLflow 3.6.0 Security

MLflow 3.6.0 introduced a security middleware that validates the `Host` header to prevent DNS rebinding attacks. This is good for security but breaks Docker container-to-container communication where hostnames don't match.

**Workaround**: Use a reverse proxy to rewrite the Host header to an accepted value.

### 2. Docker User Management

The `jupyter/datascience-notebook` image uses a complex user setup:
- Container runs as `root` (if `user: root` specified)
- Entrypoint uses `sudo` to drop privileges to `jovyan`
- All Jupyter processes run as `jovyan` (UID 1000)
- File permissions must match the `jovyan` user, not root

**Key Variables**:
- `NB_UID` - Set user ID for jovyan
- `NB_GID` - Set group ID for jovyan
- `GRANT_SUDO` - Allow jovyan to sudo
- `CHOWN_HOME` - Fix home directory ownership on startup

### 3. Python Dependency Resolution

pip's dependency resolver doesn't always find compatible versions when you specify conflicting ranges. Better to let packages install their own dependencies in order:

1. Install core framework (MLflow) first
2. Let it pull compatible dependencies
3. Then install additional packages

### 4. Volume Sharing

For MLflow artifacts to work properly:
- MLflow service needs read access (for serving)
- Jupyter service needs write access (for logging)
- Use named volume mounted to both services
- Fix ownership after container startup

---

## Quick Reference

### Start Everything

```bash
cd /Users/justin/enterprise-ai-workflows/project2-mlops-pipeline
docker-compose up -d
docker exec mlops-jupyter chown -R jovyan:users /mlflow  # Fix permissions
```

### Access Services

- **MLflow UI**: http://localhost:5000
- **MLflow Proxy**: http://localhost:5001
- **Jupyter Lab**: http://localhost:8888
- **API Docs**: http://localhost:8000/docs

### Useful Commands

```bash
# Check logs
docker-compose logs -f mlflow
docker-compose logs -f jupyter

# Check MLflow proxy
docker exec mlops-jupyter curl -I http://mlflow-proxy/

# Check permissions
docker exec mlops-jupyter ls -la /mlflow/

# Fix permissions if needed
docker exec mlops-jupyter chown -R jovyan:users /mlflow

# Restart services
docker-compose restart jupyter
docker-compose restart mlflow
```

---

## Git Commit

Committed all changes with message:
```
Fix MLflow 3.6.0 Host header validation and artifact permissions

Major Changes:
- Added nginx reverse proxy (mlflow-proxy) to handle MLflow 3.6.0 Host header validation
- Fixed artifact write permissions for Jupyter kernel (jovyan user)
- Simplified package installation to avoid dependency conflicts
```

Pushed to: https://github.com/justin-mbca/enterprise-ai-workflows

---

## Next Steps (Optional Improvements)

1. **Pre-bake Dependencies** (from TODO list)
   - Create custom Jupyter image with MLflow pre-installed
   - Create custom MLflow image with all deps
   - Eliminates cell 2 install time (~30-60 seconds)

2. **Persistent Permissions**
   - Add init container or entrypoint script to set ownership automatically
   - Avoids manual `chown` command after container startup

3. **Health Checks**
   - Add health check to mlflow-proxy
   - Verify proxy is working before Jupyter starts

4. **Environment Variables**
   - Consider using `.env` file for Docker Compose
   - Makes configuration more portable

---

**Session completed**: November 16, 2025  
**Status**: ✅ All systems working  
**Pushed to**: GitHub (commit 43e3948)
