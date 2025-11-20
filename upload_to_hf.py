#!/usr/bin/env python3
"""Manually upload project3-document-qa to Hugging Face Space"""
import os
from huggingface_hub import HfApi

# Configuration
REPO_ID = "zhangju2023/document-qa-rag"
LOCAL_FOLDER = "project3-document-qa"

def main():
    token = os.getenv("HF_TOKEN")
    if not token:
        print("❌ HF_TOKEN environment variable not set!")
        print("Run: export HF_TOKEN=your_token_here")
        return
    
    api = HfApi()
    
    print(f"📤 Uploading {LOCAL_FOLDER} to {REPO_ID}...")
    
    # Upload the entire folder
    api.upload_folder(
        folder_path=LOCAL_FOLDER,
        repo_id=REPO_ID,
        repo_type="space",
        token=token,
        commit_message="fix: switch to context extraction for factual HR questions"
    )
    
    print(f"✅ Upload complete!")
    print(f"🔗 Space will rebuild at: https://huggingface.co/spaces/{REPO_ID}")
    print("⏳ Wait 1-2 minutes for rebuild, then hard refresh (Cmd+Shift+R)")

if __name__ == "__main__":
    main()
