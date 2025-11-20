#!/bin/bash
# Manual upload script for Project 3 to Hugging Face Space

echo "Installing huggingface_hub..."
pip3 install huggingface_hub==0.24.6 -q

echo ""
echo "To upload manually, you need to:"
echo "1. Get your HF token from: https://huggingface.co/settings/tokens"
echo "2. Run: export HF_TOKEN=your_token_here"
echo "3. Run: python3 upload_to_hf.py"
echo ""
echo "Or just wait 2-5 minutes for GitHub Actions to complete the deployment automatically."
echo "Check status at: https://github.com/justin-mbca/enterprise-ai-workflows/actions"
