# Update Your Hugging Face Space

## What Changed
✅ **Added Demo Mode** - FastAPI now works WITHOUT requiring trained models
✅ **Fixed Nginx routing** - OpenAPI spec now loads correctly
✅ **Updated README** - Better documentation

## Files to Update in Your Space

Upload these files from `project2-mlops-pipeline/hf-space/` to your Space:

1. **Dockerfile** - Copies `main_demo.py` into the image
2. **main_demo.py** - FastAPI with demo predictions (+ HR endpoints)
3. **start.sh** - Runs Nginx + MLflow + API in demo mode
4. **README.md** - Updated with demo mode + HR endpoints info

## How to Update

### Option 1: Upload via Web UI (Easiest)
1. Go to: https://huggingface.co/spaces/zhangju2023/mlops-pipeline-demo
2. Click "Files" tab
3. Upload each file (drag & drop or click upload)
4. Commit changes - Space will rebuild automatically
5. Wait 2-3 minutes for rebuild

### Option 2: Git Clone (Advanced)
```bash
git clone https://huggingface.co/spaces/zhangju2023/mlops-pipeline-demo
cd mlops-pipeline-demo
# Copy files from your repo
cp /path/to/enterprise-ai-workflows/project2-mlops-pipeline/hf-space/* .
git add .
git commit -m "Update to demo mode"
git push
```

## After Update

Test these URLs (should all work now):
- ✅ https://zhangju2023-mlops-pipeline-demo.hf.space/mlflow/
- ✅ https://zhangju2023-mlops-pipeline-demo.hf.space/api/docs
- ✅ https://zhangju2023-mlops-pipeline-demo.hf.space/api/health
- ✅ https://zhangju2023-mlops-pipeline-demo.hf.space/api/predict/example
 - ✅ HR endpoints:
   - `POST` https://zhangju2023-mlops-pipeline-demo.hf.space/api/hr/payroll/forecast
   - `POST` https://zhangju2023-mlops-pipeline-demo.hf.space/api/hr/attrition/score
   - `GET`  https://zhangju2023-mlops-pipeline-demo.hf.space/api/hr/overtime-flag?weekly_hours=45

## What You'll See

**Health Check** (`/api/health`):
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "customer_churn_model",
  "model_version": "demo-v1.0",
  "mlflow_uri": "http://127.0.0.1:5000",
  "demo_mode": true
}
```

**API Docs** (`/api/docs`): Interactive FastAPI documentation with all endpoints working

**Example Prediction** (`/api/predict/example`): Returns a demo prediction

## Demo Mode Features

- 🎭 Works without trained models
- 🎯 Realistic rule-based predictions
- 📊 All API endpoints functional
- 🔄 Can switch to real models later

## Troubleshooting

**If 502 Bad Gateway persists:**
1. Check Space logs (Logs tab)
2. Look for Python errors in startup
3. Verify all 4 files uploaded correctly

**If OpenAPI still shows 404:**
1. Make sure nginx.conf.template was updated (from previous fix)
2. Check Nginx logs in Space

**Files don't match:**
Pull latest from GitHub: https://github.com/justin-mbca/enterprise-ai-workflows/tree/main/project2-mlops-pipeline/hf-space
