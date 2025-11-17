# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=7860 \
    MODEL_NAME=customer_churn_model \
    MODEL_STAGE=Production \
    MLFLOW_BACKEND_URI=sqlite:////data/mlflow.db \
    MLFLOW_ARTIFACT_ROOT=/data/artifacts

RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx git build-essential gettext-base && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone the repo with the application code
RUN git clone https://github.com/justin-mbca/enterprise-ai-workflows.git /app/repo

# Install Python dependencies (API + MLflow)
RUN pip install --upgrade pip && \
    pip install -r /app/repo/project2-mlops-pipeline/deployment/requirements.txt && \
    pip install mlflow==3.6.0 uvicorn

# Copy Nginx config template and startup script
COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Create data directories for MLflow
RUN mkdir -p /data/artifacts

EXPOSE 7860

CMD ["/bin/bash", "/start.sh"]