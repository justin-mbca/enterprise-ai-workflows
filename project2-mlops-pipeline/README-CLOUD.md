# Project 2: Cloud Deployment Guide (VM-based)

This guide shows how to deploy the complete MLOps stack (MLflow + Jupyter + FastAPI + Postgres + nginx proxy) on a small cloud VM using Docker Compose.

Works on: Ubuntu 22.04+ (Azure, AWS, GCP, DigitalOcean)

## 1) Provision a VM

- Size: 2 vCPU, 4 GB RAM (minimum)
- OS: Ubuntu 22.04 LTS
- Open inbound ports: 5000 (MLflow), 5001 (mlflow proxy), 8000 (API), 8888 (Jupyter)

## 2) One-line install & run

SSH to your VM and run:

```bash
sudo bash -lc "curl -fsSL https://raw.githubusercontent.com/justin-mbca/enterprise-ai-workflows/main/project2-mlops-pipeline/deploy/cloud-deploy.sh | bash"
```

This will:
- Install Docker Engine + Compose plugin
- Clone this repo (main branch)
- Start all services with `docker compose up -d`
- Open firewall ports (if UFW is installed)

### Optional: Terraform one-click for AWS

Prefer IaC? Use the Terraform config to provision an EC2 VM and auto-run the deploy script:

```bash
cd project2-mlops-pipeline/deploy/terraform/aws
terraform init
terraform apply -auto-approve -var "key_name=<YOUR_KEYPAIR_NAME>"
```

Outputs will include public IP and service URLs.

## 3) Access services

- MLflow UI:           http://<server-ip>:5000
- MLflow Proxy (for Jupyter): http://<server-ip>:5001
- Jupyter Lab:         http://<server-ip>:8888
- Model API (FastAPI): http://<server-ip>:8000/docs

## 4) Common operations

```bash
# Check status
cd enterprise-ai-workflows/project2-mlops-pipeline
sudo docker compose ps

# Tail logs
sudo docker compose logs -f

# Restart
sudo docker compose restart

# Stop
sudo docker compose down
```

## 5) Security notes

- This setup is for demos. For production, add auth in front of Jupyter and MLflow.
- Consider placing a TLS-terminating reverse proxy (Caddy/Traefik) in front of services.
- Use cloud security groups to restrict access by IP where appropriate.

## 6) Troubleshooting

- If MLflow shows "Invalid Host header" errors, ensure you're accessing via the proxy (port 5001) from Jupyter.
- If artifacts fail to log, ensure the `/mlflow` path inside the Jupyter container is writable by the `jovyan` user. You can run:
  ```bash
  sudo docker exec mlops-jupyter chown -R jovyan:users /mlflow
  ```
- If containers fail to start due to port conflicts, change the published ports in `docker-compose.yml`.
 - If your cloud provider blocks ports, confirm the security group / firewall allows inbound 5000, 5001, 8000, 8888 (and 22 for SSH).

## 7) Clean up

```bash
sudo docker compose down -v   # remove containers and volumes
sudo apt-get remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

---

If you'd like a managed deployment (Azure Container Apps / ECS / Cloud Run), we can add IaC templates next.
