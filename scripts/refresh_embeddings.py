"""Refresh Chroma embeddings from dbt DuckDB outputs.

Placeholder script: In CI this would
1. Query document_index model from DuckDB.
2. Rebuild vector store (Chroma) used by project3-document-qa.
3. Optionally trigger HF Space upload.

For now, it prints row counts to prove connectivity.
"""
import duckdb
import os

DUCKDB_PATH = "data-platform/dbt/warehouse/data.duckdb"
MODEL_TABLE = "document_index"

def main():
    if not os.path.exists(DUCKDB_PATH):
        print(f"DuckDB file not found at {DUCKDB_PATH}. Run dbt first.")
        return
    con = duckdb.connect(DUCKDB_PATH)
    try:
        if MODEL_TABLE not in [r[0] for r in con.execute("show tables").fetchall()]:
            print(f"Table {MODEL_TABLE} not found. Ensure dbt run completed.")
            return
        count = con.execute(f"select count(*) from {MODEL_TABLE}").fetchone()[0]
        print(f"document_index rows: {count}")
    finally:
        con.close()

if __name__ == "__main__":
    main()
