# Update Your Hugging Face Space (RAG)

This guide helps you update your existing Space to reflect the new HR policy features (sample corpus + loader button).

## What Changed

- Added "Load Sample HR Policy Documents" in the Manage Documents tab
- Included curated HR policy snippets (PTO, overtime, payroll schedule, benefits, FMLA, expenses, reviews)
- Minor README improvements

## Files to Update in Your Space

Upload these 3 files from this repo to your Space:

1. `project3-document-qa/app.py`
2. `project3-document-qa/requirements.txt`
3. (optional) `project3-document-qa/README.md`

## Option A — Upload via Web UI (Easiest)

1. Go to your Space: https://huggingface.co/spaces/zhangju2023/document-qa-rag
2. Click the "Files" tab
3. Upload the files listed above (drag & drop or click Upload)
4. Commit the changes — the Space will rebuild automatically
5. Wait 1–3 minutes for the rebuild

## Option B — Link to GitHub (Recommended)

1. In your Space, open "Settings" → "Repository" → "Link Git Repositories"
2. Connect GitHub repo: `justin-mbca/enterprise-ai-workflows`
3. Map the subdirectory: `/project3-document-qa`
4. App file: `app.py` (Gradio)
5. Save. The Space will auto-sync on every push to `main`.

## After Update — Quick Test

In the running app:

- Go to "📁 Manage Documents"
- Click "📥 Load Sample HR Policy Documents" → wait for success
- Switch to "💬 Ask Questions" and try:
  - "What is the overtime policy?"
  - "When is payroll processed?"
  - "How does PTO accrue?"

If you see "No relevant documents", ensure you loaded the HR sample first.

## Troubleshooting

- First load can take 1–3 minutes while models download
- If the Space errors, check Logs → look for package install or model download issues
- You can switch to a lighter LLM in `app.py` (e.g., `sshleifer/tiny-gpt2`) to reduce cold start time
