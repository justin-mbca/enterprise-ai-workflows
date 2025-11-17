"""
Seed MLflow with a demo pyfunc model and register it as `customer_churn_model` in Production.
Safe to run multiple times (idempotent): if a Production version exists, it will skip.
"""
from __future__ import annotations

import time
import os
import logging
from typing import Any

import mlflow
import mlflow.pyfunc
from mlflow.tracking import MlflowClient

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("seed_mlflow")

TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "customer_churn_model")
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT", "Churn Demo")


class DemoChurnModel(mlflow.pyfunc.PythonModel):
    """A tiny rule-based churn model for demo purposes."""

    def predict(self, context, model_input):
        import numpy as np
        import pandas as pd

        if isinstance(model_input, dict):
            df = pd.DataFrame([model_input])
        else:
            df = pd.DataFrame(model_input)

        preds = []
        for _, row in df.iterrows():
            score = 0.0
            if float(row.get("monthly_charges", 0)) > 80:
                score += 0.3
            if float(row.get("tenure", 0)) < 12:
                score += 0.3
            if str(row.get("contract_type", "")) == "Month-to-month":
                score += 0.2
            if str(row.get("online_security", "")) == "No":
                score += 0.1
            if str(row.get("tech_support", "")) == "No":
                score += 0.1
            score = max(0.0, min(1.0, score))
            pred = 1 if score > 0.5 else 0
            preds.append(pred)
        return preds


def ensure_mlflow_ready(timeout_s: int = 60) -> None:
    mlflow.set_tracking_uri(TRACKING_URI)
    client = MlflowClient(TRACKING_URI)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            _ = client.list_experiments()
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("MLflow tracking server not reachable")


def production_version_exists(client: MlflowClient, name: str) -> bool:
    try:
        vers = client.get_latest_versions(name, stages=["Production"]) or []
        return len(vers) > 0
    except Exception:
        return False


def main() -> None:
    log.info("Seeding MLflow demo model if needed…")
    ensure_mlflow_ready()
    mlflow.set_tracking_uri(TRACKING_URI)
    client = MlflowClient(TRACKING_URI)

    # Skip if Production already exists
    if production_version_exists(client, MODEL_NAME):
        log.info("Model %s already has a Production version. Skipping seeding.", MODEL_NAME)
        return

    # Create or get experiment
    exp = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if not exp:
        exp_id = mlflow.create_experiment(EXPERIMENT_NAME)
    else:
        exp_id = exp.experiment_id

    with mlflow.start_run(experiment_id=exp_id) as run:
        mlflow.set_tag("purpose", "demo")
        mlflow.log_param("demo", True)

        # Log a pyfunc model
        python_model = DemoChurnModel()
        mlflow.pyfunc.log_model(
            artifact_path="model",
            python_model=python_model,
            pip_requirements=[
                "mlflow",
                "pandas",
                "numpy",
                "cloudpickle",
            ],
        )

        model_uri = f"runs:/{run.info.run_id}/model"
        log.info("Registering model %s from %s", MODEL_NAME, model_uri)
        result = mlflow.register_model(model_uri=model_uri, name=MODEL_NAME)

    # Transition to Production
    # Registry ops can be eventually consistent; poll briefly until visible
    for _ in range(30):
        try:
            client.transition_model_version_stage(
                name=MODEL_NAME, version=result.version, stage="Production", archive_existing_versions=False
            )
            log.info("Promoted %s v%s to Production", MODEL_NAME, result.version)
            break
        except Exception as e:
            time.sleep(1)
    else:
        log.warning("Could not promote model to Production; check MLflow UI.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.exception("Seeding failed: %s", e)
        raise
