#!/usr/bin/env bash
# Cloud deployment script for Project 2 (MLOps Pipeline)
# Target: Ubuntu 22.04+ VM with public IP
# Usage: curl -fsSL https://raw.githubusercontent.com/justin-mbca/enterprise-ai-workflows/main/project2-mlops-pipeline/deploy/cloud-deploy.sh | bash

set -euo pipefail

# Config
REPO_URL="https://github.com/justin-mbca/enterprise-ai-workflows.git"
REPO_DIR="enterprise-ai-workflows"
PROJECT_DIR="project2-mlops-pipeline"
BRANCH="main"

print_header() {
  echo "\n=============================================="
  echo "$1"
  echo "==============================================\n"
}

require_root() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "Please run as root (use sudo)."
    exit 1
  fi
}

install_docker() {
  print_header "Installing Docker Engine and Compose"
  apt-get update -y
  apt-get install -y ca-certificates curl gnupg lsb-release
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  systemctl enable --now docker
}

clone_repo() {
  print_header "Fetching repository"
  if ! command -v git >/dev/null 2>&1; then
    apt-get install -y git
  fi
  if [ ! -d "$REPO_DIR" ]; then
    git clone --depth 1 -b "$BRANCH" "$REPO_URL"
  fi
  cd "$REPO_DIR/$PROJECT_DIR"
}

open_firewall() {
  if command -v ufw >/dev/null 2>&1; then
    print_header "Configuring UFW firewall (allow 5000,5001,8000,8888)"
    ufw allow 5000/tcp || true
    ufw allow 5001/tcp || true
    ufw allow 8000/tcp || true
    ufw allow 8888/tcp || true
  fi
}

start_stack() {
  print_header "Starting MLOps stack with Docker Compose"
  docker compose pull || true
  docker compose up -d
  docker compose ps
}

print_endpoints() {
  IP=$(curl -s ifconfig.me || echo "<your-server-ip>")
  print_header "Deployment complete"
  cat <<EOF
Services are starting. Access them via:
- MLflow UI:           http://$IP:5000
- MLflow Proxy (Jupy): http://$IP:5001
- Jupyter Lab:         http://$IP:8888
- Model API (FastAPI): http://$IP:8000/docs

Tips:
- If Jupyter needs a token-less login, it's already configured.
- Ensure security groups/firewall allow inbound TCP: 5000,5001,8000,8888.
- To see logs: docker compose logs -f
- To stop:      docker compose down
EOF
}

main() {
  require_root
  install_docker
  clone_repo
  open_firewall
  start_stack
  print_endpoints
}

main "$@"
