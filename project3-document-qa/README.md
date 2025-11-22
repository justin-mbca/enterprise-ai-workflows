---
title: Document Q&A (RAG)
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "4.39.0"
app_file: app.py
pinned: false
---

# Project 3: Document Q&A (Gradio / Hugging Face Spaces)

[![Open in Hugging Face Spaces](https://img.shields.io/badge/Spaces-Open%20App-blue?logo=huggingface)](https://huggingface.co/spaces/zhangju2023/document-qa-rag)

A RAG (Retrieval-Augmented Generation) application using:
- ChromaDB for vector storage
- SentenceTransformers for embeddings (`all-MiniLM-L6-v2`)
- Hugging Face Transformers for text generation (`distilgpt2`)
- Gradio UI

## Local Run

```bash
cd project3-document-qa
pip install -r requirements.txt
export CHROMA_PERSIST_DIR="project3-document-qa/chroma_store"  # optional; defaults internally
python ../scripts/refresh_embeddings.py --persist-dir "$CHROMA_PERSIST_DIR" --reset
python app.py
# Then open http://localhost:7860
```

Live app: https://huggingface.co/spaces/zhangju2023/document-qa-rag

## Try it online (3 steps)

1) Open the Space
   - https://huggingface.co/spaces/zhangju2023/document-qa-rag
   - First load can take 1–3 minutes while models download

2) Load documents
   - Go to the "📁 Manage Documents" tab
   - Click "📥 Load Sample AI/ML Documents" or "📥 Load Sample HR Policy Documents" and wait for the status to confirm
   - (Optional) Paste your own text into "Document Text" and click "➕ Add Document"

3) Ask a question
   - Switch to the "💬 Ask Questions" tab
   - Type a question or click one of the sample buttons
   - Adjust "Number of context documents" if you like (default: 3)
   - Click "🔍 Ask Question" and read the answer
   - Expand "📄 Retrieved Context" to see the sources and relevance scores

Troubleshooting
- HR use case tips:
   - Try questions like "What is the overtime policy?", "When is payroll processed?", or "How does PTO accrue?"
   - Load the HR sample first to populate the knowledge base with HR/policy docs.
- If you see "No relevant documents", make sure you loaded sample or custom documents
- First inference might be slow while the model warms up; later queries are faster
- Click "📊 View Statistics" or "🗑️ Clear Knowledge Base" in the Manage tab to inspect/reset the index

## CI/CD (Auto-deploy from GitHub)

This folder is configured to auto-sync to the Hugging Face Space via GitHub Actions.

- Workflow: `.github/workflows/deploy-project3-to-hf.yml`
- Trigger: Any push to `main` that changes files under `project3-document-qa/**`
- Requirements: GitHub repo secret `HF_TOKEN` containing a Hugging Face write token
- Target Space: `zhangju2023/document-qa-rag`

If you just pushed changes and don't see them live yet:
1. Open the GitHub "Actions" tab and check the latest run for "Deploy Project 3 (RAG) to Hugging Face Space".
2. Wait 1–3 minutes for the Space to rebuild after the upload completes.
3. Hard refresh the Space page (Cmd+Shift+R) if the UI was open during the update.

## Deploy to Hugging Face Spaces

Option A — Create a new Space and upload:
1. Go to https://huggingface.co/spaces
2. New Space → Type: "Gradio" → Name: `document-qa-rag`
3. Upload these files from this repo:
   - `project3-document-qa/app.py`
   - `project3-document-qa/requirements.txt`
   - (optional) `README.md`
4. Set the Space hardware to CPU Basic (free)
5. The app will auto-build and launch

Option B — Connect to GitHub (recommended):
1. Create a new Space as above
2. In Space settings → "Link Git Repositories"
3. Connect to this GitHub repo and map `/project3-document-qa` folder
4. Set `app.py` as the entry file

Notes:
- First build may take a while to download models.
- You can switch to a lighter LLM in `app.py` (e.g., `sshleifer/tiny-gpt2`) if needed.
- For production, consider larger models via Inference Endpoints or OpenAI with an API key.

## Embedding Refresh (dbt-integrated)

The RAG layer can ingest curated documents produced by the dbt data platform (`document_index` mart).

### Pre-requisites
1. Run dbt to build the `document_index` view:
   ```bash
   cd data-platform/dbt
   dbt seed && dbt run
   ```
2. Ensure the DuckDB file exists at `data-platform/dbt/warehouse/data.duckdb`.

### Build / Rebuild Vector Store
```bash
export CHROMA_PERSIST_DIR="project3-document-qa/chroma_store"  # choose any directory
python scripts/refresh_embeddings.py --persist-dir "$CHROMA_PERSIST_DIR" --reset
```

Flags:
- `--reset` (optional): clears existing collection before loading
- `--limit N` (optional): ingest only first N rows for quick tests
- `--duckdb PATH`: override DuckDB file location
- `--collection NAME`: change Chroma collection name (default: `documents`)

### Launch App Using Persisted Embeddings
```bash
cd project3-document-qa
export CHROMA_PERSIST_DIR="project3-document-qa/chroma_store"
python app.py
```

At startup the app detects a persistent store and **skips adding sample documents**, using the dbt-derived corpus instead.

### Updating Embeddings After dbt Changes
If you modify source seeds or transformation logic:
```bash
cd data-platform/dbt
dbt seed && dbt run
cd ../../
python scripts/refresh_embeddings.py --persist-dir "$CHROMA_PERSIST_DIR" --reset
```

### Common Issues
| Symptom | Cause | Fix |
|---------|-------|-----|
| `DuckDB file not found` | dbt not executed | Run `dbt seed && dbt run` |
| Empty collection after refresh | `document_index` view missing | Confirm model name and rerun dbt |
| App still shows sample docs | Persist dir not set or empty | Export `CHROMA_PERSIST_DIR` and rebuild embeddings |
| Duplicate ID errors | Re-running without `--reset` and changed IDs | Use `--reset` for full rebuild |

---
