"""Rebuild persistent Chroma vector store from the dbt `document_index` mart.

Workflow:
1. Connect to DuckDB warehouse produced by dbt.
2. Read rows from `document_index` (id, domain, text).
3. Generate embeddings with SentenceTransformers.
4. Persist vectors + metadata to a Chroma persistent directory for the Gradio RAG app.

Usage:
    python scripts/refresh_embeddings.py --persist-dir project3-document-qa/chroma_store --reset

Flags:
    --persist-dir   Path for Chroma persistent directory (default: project3-document-qa/chroma_store)
    --duckdb        Path to DuckDB file (default: data-platform/dbt/warehouse/data.duckdb)
    --reset         If supplied, deletes existing collection before rebuild
    --collection    Collection name (default: documents)
    --limit         Optional cap on number of rows ingested (for quick tests)

After running, start the app:
    cd project3-document-qa && python app.py
The app will detect existing stored embeddings and skip sample preload.
"""
from __future__ import annotations
import argparse
import os
import duckdb
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict

DEFAULT_DUCKDB_PATH = "data-platform/dbt/warehouse/data.duckdb"
MODEL_TABLE = "document_index"  # base name; may be schema-qualified (e.g., main_marts.document_index)
DEFAULT_PERSIST_DIR = "project3-document-qa/chroma_store"
DEFAULT_COLLECTION = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_rows(con: duckdb.DuckDBPyConnection, table_name: str, limit: int | None = None) -> List[Dict]:
    sql = f"SELECT id, domain, text FROM {table_name} ORDER BY id"
    if limit:
        sql += f" LIMIT {int(limit)}"
    data = con.execute(sql).fetchall()
    return [{"id": r[0], "domain": r[1], "text": r[2]} for r in data]


def build_vector_store(rows: List[Dict], persist_dir: str, collection: str, reset: bool = False) -> int:
    if not rows:
        print("No rows supplied to build vector store.")
        return 0

    os.makedirs(persist_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=persist_dir, settings=Settings(anonymized_telemetry=False))

    if reset:
        try:
            client.delete_collection(collection)
            print(f"🔄 Reset existing collection '{collection}'.")
        except Exception:
            pass

    try:
        col = client.get_collection(collection)
    except Exception:
        col = client.create_collection(collection, metadata={"source": "dbt_document_index"})

    # Existing IDs to avoid duplicates (incremental build)
    existing_ids = set()
    try:
        # Chroma does not offer direct listing of all IDs without pagination; attempt a count only.
        # We'll still add all; duplicates will raise so we filter first.
        # Using where filter '*' unsupported; rely on exception handling.
        pass
    except Exception:
        pass

    ids = []
    texts = []
    metas = []
    for r in rows:
        _id = str(r["id"])  # ensure string for Chroma
        if _id in existing_ids:
            continue
        ids.append(_id)
        texts.append(r["text"])
        metas.append({"domain": r["domain"], "source": "dbt"})

    print(f"Embedding {len(ids)} rows with model '{EMBEDDING_MODEL}'...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(texts, batch_size=32).tolist()

    # Chunked add to avoid large payload issues
    BATCH = 64
    for i in range(0, len(ids), BATCH):
        j = i + BATCH
        col.add(
            ids=ids[i:j],
            documents=texts[i:j],
            metadatas=metas[i:j],
            embeddings=embeddings[i:j]
        )
        print(f"Added {min(j, len(ids))}/{len(ids)} embeddings...")

    print(f"✅ Vector store build complete. Collection '{collection}' now has {col.count()} documents.")
    print(f"📂 Persisted at: {persist_dir}")
    return len(ids)


def main():
    parser = argparse.ArgumentParser(description="Rebuild Chroma vector store from dbt document_index mart")
    parser.add_argument("--persist-dir", default=DEFAULT_PERSIST_DIR)
    parser.add_argument("--duckdb", default=DEFAULT_DUCKDB_PATH)
    parser.add_argument("--reset", action="store_true", help="Delete existing collection before rebuild")
    parser.add_argument("--collection", default=DEFAULT_COLLECTION)
    parser.add_argument("--limit", type=int, default=None, help="Optional limit on rows ingested")
    args = parser.parse_args()

    if not os.path.exists(args.duckdb):
        print(f"❌ DuckDB file not found at {args.duckdb}. Run dbt first (dbt seed && dbt run).")
        return

    con = duckdb.connect(args.duckdb)
    try:
        # Look for table or view via information_schema (captures views in schemas like main_marts)
        info_rows = con.execute(
            "SELECT table_schema, table_name FROM information_schema.tables WHERE table_name = ?",
            [MODEL_TABLE]
        ).fetchall()
        table_name = None
        if info_rows:
            # Pick first schema (expect one)
            schema, name = info_rows[0]
            table_name = f"{schema}.{name}" if schema else name
        else:
            # Fallback to unqualified presence in SHOW TABLES (for seeds)
            tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
            if MODEL_TABLE in tables:
                table_name = MODEL_TABLE
        if not table_name:
            tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
            print(f"❌ '{MODEL_TABLE}' not found in DuckDB (checked information_schema). Available base tables: {tables}\nRun dbt (dbt seed && dbt run) to build the mart.")
            return
        rows = load_rows(con, table_name, args.limit)
        print(f"Using table: {table_name}")
        print(f"Found {len(rows)} rows in {MODEL_TABLE}.")
    finally:
        con.close()

    build_vector_store(rows, args.persist_dir, args.collection, reset=args.reset)


if __name__ == "__main__":
    main()
