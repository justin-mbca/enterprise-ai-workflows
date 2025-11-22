#!/usr/bin/env python3
"""Generate HTML pipeline report.
Usage: python generate_pipeline_report.py <output_html> <pipeline_log_path>
"""
import sys, datetime
from pathlib import Path

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('pipeline_report.html')
log_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('pipeline_run.log')

html = ["<html><head><title>Pipeline Report</title><style>body{font-family:Arial;margin:2rem;}code{background:#f5f5f5;padding:2px 4px;}table{border-collapse:collapse;}td,th{border:1px solid #ccc;padding:4px 8px;}h2{margin-top:2rem;}pre{background:#f5f5f5;padding:1rem;overflow:auto;} .ok{color:#0a6;} .fail{color:#c00;} </style></head><body>"]
html.append("<h1>Enterprise AI Workflows - Pipeline Report</h1>")
html.append(f"<p>Generated: {datetime.datetime.utcnow().isoformat()}Z</p>")

# Warehouse metrics
duck = Path('data-platform/dbt/warehouse/data.duckdb')
if duck.exists():
    try:
        import duckdb
        con = duckdb.connect(str(duck))
        tables = ["main_marts.document_index", "main_marts.hr_policy_features", "main_marts.arbitration_timelines"]
        html.append("<h2>Mart Row Counts</h2><table><tr><th>Table</th><th>Rows</th></tr>")
        for t in tables:
            try:
                cnt = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                html.append(f"<tr><td>{t}</td><td>{cnt}</td></tr>")
            except Exception:
                html.append(f"<tr><td>{t}</td><td>error</td></tr>")
        html.append("</table>")
    except Exception as e:
        html.append(f"<p class='fail'>DuckDB analysis error: {e}</p>")
else:
    html.append("<p class='fail'>Warehouse not found.</p>")

# Vector store metrics
store = Path('project3-document-qa/chroma_store')
if store.exists():
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(store))
        col = client.get_collection('documents')
        html.append(f"<h2>Vector Store</h2><p>Collection 'documents' count: {col.count()}</p>")
    except Exception as e:
        html.append(f"<p class='fail'>Vector store error: {e}</p>")
else:
    html.append("<p class='fail'>Vector store directory not found.</p>")

# Log tail
if log_path.exists():
    try:
        with log_path.open(encoding='utf-8') as fh:
            lines = fh.read().splitlines()
        tail = lines[-80:]
        safe = '\n'.join(tail).replace('<','&lt;')
        html.append("<h2>Pipeline Log (tail)</h2><pre>" + safe + "</pre>")
    except Exception as e:
        html.append(f"<p class='fail'>Could not read log: {e}</p>")
else:
    html.append("<p class='fail'>Log file not found.</p>")

html.append("<p><a href='/'>Back to Site Index</a></p>")
html.append("</body></html>")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text('\n'.join(html), encoding='utf-8')
print(f"Report written to {out}")
