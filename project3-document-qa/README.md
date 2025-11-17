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
   - Click "📥 Load Sample AI/ML Documents" and wait for the status to confirm
   - (Optional) Paste your own text into "Document Text" and click "➕ Add Document"

3) Ask a question
   - Switch to the "💬 Ask Questions" tab
   - Type a question or click one of the sample buttons
   - Adjust "Number of context documents" if you like (default: 3)
   - Click "🔍 Ask Question" and read the answer
   - Expand "📄 Retrieved Context" to see the sources and relevance scores

Troubleshooting
- If you see "No relevant documents", make sure you loaded sample or custom documents
- First inference might be slow while the model warms up; later queries are faster
- Click "📊 View Statistics" or "🗑️ Clear Knowledge Base" in the Manage tab to inspect/reset the index

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
