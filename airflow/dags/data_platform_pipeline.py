"""Airflow DAG: data_platform_pipeline

Demonstrates orchestration of the data & RAG preparation workflow:
1. dbt seed -> build source tables
2. dbt run -> build staging + marts (including document_index)
3. dbt test -> enforce data quality
4. Refresh embeddings (build persistent Chroma store from document_index)
5. Data quality check comparing DuckDB document count vs. vector store count

This is intentionally minimal to showcase Airflow competency for portfolio purposes.

Prerequisites:
- Airflow installed with dependencies in airflow/requirements-airflow.txt
- Variable REPO_ROOT pointing to repository root (set in Airflow UI or env)
- Variable CHROMA_DIR (optional) defaults to <REPO_ROOT>/project3-document-qa/chroma_store

Set execution date schedule at 05:00 UTC daily (adjust as needed).
"""
from __future__ import annotations

from datetime import datetime, timedelta
import os

try:  # Airflow imports (will resolve inside an Airflow environment)
    from airflow import DAG  # type: ignore
    from airflow.models import Variable  # type: ignore
    from airflow.operators.bash import BashOperator  # type: ignore
    from airflow.operators.python import PythonOperator  # type: ignore
    from airflow.exceptions import AirflowFailException  # type: ignore
except ImportError:
    # Allow static analysis / non-Airflow environments to import this module without failing.
    DAG = object  # type: ignore
    Variable = object  # type: ignore
    BashOperator = object  # type: ignore
    PythonOperator = object  # type: ignore
    class AirflowFailException(Exception):  # type: ignore
        pass


def _resolve_paths():
    repo_root = Variable.get("REPO_ROOT", default_var=os.getenv("REPO_ROOT", "/Users/justin/enterprise-ai-workflows"))
    chroma_dir = Variable.get(
        "CHROMA_DIR", default_var=os.getenv("CHROMA_DIR", os.path.join(repo_root, "project3-document-qa", "chroma_store"))
    )
    return repo_root, chroma_dir


def doc_vector_count_check():
    """Ensure the number of documents in DuckDB matches number of vectors in Chroma.
    Raises AirflowFailException if mismatch exceeds tolerance.
    """
    repo_root, chroma_dir = _resolve_paths()

    try:
        import duckdb  # type: ignore
        import chromadb  # type: ignore
    except ImportError as e:
        raise AirflowFailException(f"Missing dependency for quality check: {e}") from e

    db_path = os.path.join(repo_root, "data-platform", "dbt", "warehouse", "data.duckdb")
    if not os.path.exists(db_path):
        raise AirflowFailException(f"DuckDB warehouse not found at {db_path}")

    con = duckdb.connect(db_path)
    # Try both unqualified and schema-qualified names
    doc_count = None
    for candidate in ["document_index", "main_marts.document_index"]:
        try:
            doc_count = con.execute(f"SELECT COUNT(*) FROM {candidate}").fetchone()[0]
            break
        except Exception as exc:  # narrow logging for transparency
            print(f"Attempt to query {candidate} failed: {exc}")
            continue
    if doc_count is None:
        raise AirflowFailException("Could not locate document_index (tried unqualified and schema-qualified)")

    client = chromadb.PersistentClient(path=chroma_dir)
    try:
        collection = client.get_collection("documents")
    except Exception as exc:
        raise AirflowFailException("Chroma collection 'documents' not found. Did the refresh_embeddings task run?") from exc

    # Chroma doesn't expose count directly; we rely on peek with a large limit
    vectors = collection.get(include=["embeddings"], limit=doc_count + 5)
    vector_count = len(vectors["ids"]) if vectors and "ids" in vectors else 0

    tolerance = 0  # exact match expected in this demo
    if vector_count + tolerance < doc_count:
        raise AirflowFailException(
            f"Vector store count ({vector_count}) < document_index count ({doc_count}). Embedding refresh may have failed."
        )

    print(f"Document count check passed: {doc_count} documents, {vector_count} vectors.")


def build_bash_command(command: str) -> str:
    repo_root, _ = _resolve_paths()
    # Ensure we cd into the correct directory for dbt commands
    return f"cd {repo_root}/data-platform/dbt && {command}"


def build_refresh_embeddings_command() -> str:
    repo_root, chroma_dir = _resolve_paths()
    script = os.path.join(repo_root, "scripts", "refresh_embeddings.py")
    return f"python {script} --persist-dir {chroma_dir} --reset"


default_args = {
    "owner": "data-platform",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="data_platform_pipeline",
    description="Daily build of dbt marts + embeddings + quality checks",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 5 * * *",  # 05:00 UTC daily
    catchup=False,
    default_args=default_args,
    tags=["dbt", "rag", "embeddings", "portfolio"],
) as dag:

    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command=build_bash_command("dbt seed --no-write-json"),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=build_bash_command("dbt run"),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=build_bash_command("dbt test"),
    )

    ge_validate = BashOperator(
        task_id="ge_document_index_validation",
        bash_command=(
            f"cd {_resolve_paths()[0]} && "
            "REPO_ROOT=$(pwd) great_expectations checkpoint run document_index_checkpoint"
        ),
    )

    refresh_embeddings = BashOperator(
        task_id="refresh_embeddings",
        bash_command=build_refresh_embeddings_command(),
    )

    quality_check = PythonOperator(
        task_id="doc_vector_count_check",
        python_callable=doc_vector_count_check,
    )

    # DAG dependencies
    dbt_seed >> dbt_run >> dbt_test >> ge_validate >> refresh_embeddings >> quality_check
