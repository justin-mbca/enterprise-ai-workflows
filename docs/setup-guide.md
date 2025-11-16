# 🚀 Complete Setup Guide

This guide will help you set up all three enterprise AI workflow projects on your local machine.

## 📋 Prerequisites

### Required Software

1. **Python 3.8 or higher**
   ```bash
   python3 --version
   ```

2. **Docker Desktop** (for Project 2 only)
   - Download from: https://www.docker.com/products/docker-desktop/
   - Verify installation:
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Git** (for version control)
   ```bash
   git --version
   ```

### System Requirements

- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: 5GB free space
- **OS**: macOS, Linux, or Windows with WSL2

---

## 🎯 Quick Start (All Projects)

### Step 1: Clone or Navigate to Repository

```bash
cd /Users/justin/enterprise-ai-workflows
```

### Step 2: Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR on Windows:
# venv\Scripts\activate
```

### Step 3: Upgrade pip

```bash
pip install --upgrade pip
```

---

## 📊 Project 1: Rapid Insights Workflow

**Simulates:** Snowflake Cortex AI  
**Time to setup:** ~5 minutes  
**Difficulty:** ⭐ Easy

### Installation

```bash
cd project1-rapid-insights

# Install dependencies
pip install -r requirements.txt

# This will install:
# - Streamlit (web framework)
# - TextBlob (NLP)
# - Prophet (forecasting)
# - Plotly (visualization)
```

### Running the Application

```bash
streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`

### Features to Try

1. **Sentiment Analysis**
   - Analyze individual text
   - Upload CSV for batch processing
   - View sentiment distributions

2. **Time Series Forecasting**
   - Generate sample data
   - View forecasts with confidence intervals
   - Download predictions

3. **SQL Playground**
   - Use custom AI functions in SQL
   - Try `sentiment_analysis(text)`
   - Try `summarize_text(text, num_sentences)`

### Troubleshooting

**Issue**: Prophet installation fails
```bash
# Install build tools first (macOS)
brew install cmake

# Or use conda instead
conda install -c conda-forge prophet
```

**Issue**: TextBlob errors
```bash
# Download required corpora
python -m textblob.download_corpora
```

---

## 🤖 Project 2: Enterprise MLOps Pipeline

**Simulates:** Azure ML, Dataiku  
**Time to setup:** ~15 minutes  
**Difficulty:** ⭐⭐ Moderate

### Installation

```bash
cd project2-mlops-pipeline

# Install Python dependencies (optional, runs in containers)
pip install -r deployment/requirements.txt
```

### Starting the Platform

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

**Services will be available at:**
- **MLflow UI**: http://localhost:5000
- **Jupyter Lab**: http://localhost:8888
- **FastAPI Docs**: http://localhost:8000/docs

### Using Jupyter Lab

1. Open http://localhost:8888 (no password required)
2. Navigate to `work/` folder
3. Open `01_customer_churn_mlops.ipynb`
4. Run all cells to train models

### Viewing Experiments in MLflow

1. Open http://localhost:5000
2. Click on "customer-churn-prediction" experiment
3. Compare different model runs
4. View metrics, parameters, and artifacts

### Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Make a prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "tenure": 12,
      "monthly_charges": 70.50,
      "total_charges": 846.00,
      "contract_type": "Month-to-month",
      "payment_method": "Electronic check",
      "internet_service": "Fiber optic",
      "online_security": "No",
      "tech_support": "No"
    }
  }'

# Or visit interactive docs at:
# http://localhost:8000/docs
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears all data)
docker-compose down -v
```

### Troubleshooting

**Issue**: Ports already in use
```bash
# Check what's using the ports
lsof -i :5000  # MLflow
lsof -i :8888  # Jupyter
lsof -i :8000  # FastAPI

# Kill the process or change ports in docker-compose.yml
```

**Issue**: Docker out of memory
```bash
# Increase Docker memory in Docker Desktop settings
# Preferences → Resources → Memory → 4GB or more
```

**Issue**: Model not loading in API
```bash
# Make sure to run the Jupyter notebook first to train and register a model
# The API expects a model named "customer_churn_model" in Production stage
```

---

## 💬 Project 3: Document Q&A System

**Simulates:** Azure OpenAI + Azure Cognitive Search  
**Time to setup:** ~10 minutes (first run downloads models)  
**Difficulty:** ⭐⭐ Moderate

### Installation

```bash
cd project3-document-qa

# Install dependencies
pip install -r requirements.txt

# Note: First run will download models (~500MB):
# - all-MiniLM-L6-v2 (embedding model)
# - distilgpt2 (language model)
```

### Running the Application

```bash
python app.py
```

Access the interface at: `http://localhost:7860`

### Using the System

1. **Load Sample Documents**
   - Go to "Manage Documents" tab
   - Click "Load Sample AI/ML Documents"
   - Loads 8 documents about AI/ML topics

2. **Ask Questions**
   - Go to "Ask Questions" tab
   - Type a question or use sample questions
   - View answer and retrieved context

3. **Add Custom Documents**
   - Go to "Manage Documents" tab
   - Paste your own document text
   - Click "Add Document"

### Sample Questions to Try

- "What is machine learning?"
- "Explain deep learning"
- "What is the transformer architecture?"
- "How does MLOps work?"
- "What is the difference between containers and virtual machines?"

### Troubleshooting

**Issue**: Model download slow/fails
```bash
# Download models manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('distilgpt2'); AutoModelForCausalLM.from_pretrained('distilgpt2')"
```

**Issue**: Out of memory
```bash
# Use smaller batch size or lighter model
# Edit app.py and change llm_model_name to "distilgpt2" (already default)
```

**Issue**: Answers are nonsensical
```bash
# This is expected with DistilGPT-2 (small model)
# For better results, upgrade to:
# - "gpt2-medium" or "gpt2-large" (more memory required)
# - "facebook/opt-1.3b" (even better, but needs GPU)
```

---

## 🧪 Testing All Projects

### Quick Test Script

Create a file `test_all.sh`:

```bash
#!/bin/bash

echo "Testing all projects..."

# Test Project 1
echo "1. Testing Rapid Insights..."
cd project1-rapid-insights
python -c "from database import DatabaseManager; db = DatabaseManager(); print('✅ Project 1 OK')"
cd ..

# Test Project 2
echo "2. Testing MLOps Pipeline..."
docker-compose -f project2-mlops-pipeline/docker-compose.yml config > /dev/null && echo "✅ Project 2 Config OK"

# Test Project 3
echo "3. Testing Document Q&A..."
cd project3-document-qa
python -c "import chromadb; print('✅ Project 3 OK')"
cd ..

echo "All tests passed! 🎉"
```

Make it executable and run:

```bash
chmod +x test_all.sh
./test_all.sh
```

---

## 📦 Installing Everything at Once

### Master Installation Script

Create `install_all.sh`:

```bash
#!/bin/bash

echo "🚀 Installing all enterprise AI workflow projects..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Project 1
echo "📊 Installing Project 1..."
pip install -r project1-rapid-insights/requirements.txt

# Install Project 2 (Python dependencies only)
echo "🤖 Installing Project 2..."
pip install -r project2-mlops-pipeline/deployment/requirements.txt

# Install Project 3
echo "💬 Installing Project 3..."
pip install -r project3-document-qa/requirements.txt

echo "✅ All projects installed!"
echo ""
echo "Next steps:"
echo "1. For Project 1: cd project1-rapid-insights && streamlit run app.py"
echo "2. For Project 2: cd project2-mlops-pipeline && docker-compose up -d"
echo "3. For Project 3: cd project3-document-qa && python app.py"
```

Run it:

```bash
chmod +x install_all.sh
./install_all.sh
```

---

## 🐳 Docker-Only Setup (Alternative)

If you prefer running everything in Docker:

### Project 1 Dockerfile

Create `project1-rapid-insights/Dockerfile`:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Run:
```bash
docker build -t rapid-insights .
docker run -p 8501:8501 rapid-insights
```

### Project 3 Dockerfile

Create `project3-document-qa/Dockerfile`:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python", "app.py"]
```

Run:
```bash
docker build -t document-qa .
docker run -p 7860:7860 document-qa
```

---

## 🔧 Common Issues & Solutions

### Python Version Issues

```bash
# Use pyenv to manage Python versions
brew install pyenv
pyenv install 3.10.0
pyenv local 3.10.0
```

### Permission Denied on Mac

```bash
# Fix permissions
sudo chown -R $(whoami) /Users/justin/enterprise-ai-workflows
```

### Disk Space Issues

```bash
# Clean Docker
docker system prune -a

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
```

### Port Conflicts

```bash
# Find and kill processes using ports
lsof -ti:8501 | xargs kill  # Streamlit
lsof -ti:8888 | xargs kill  # Jupyter
lsof -ti:5000 | xargs kill  # MLflow
lsof -ti:8000 | xargs kill  # FastAPI
lsof -ti:7860 | xargs kill  # Gradio
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Project 1 loads at http://localhost:8501
- [ ] Can analyze sentiment in Project 1
- [ ] Project 2 MLflow loads at http://localhost:5000
- [ ] Project 2 Jupyter loads at http://localhost:8888
- [ ] Can train model in Jupyter notebook
- [ ] Project 2 API docs load at http://localhost:8000/docs
- [ ] Project 3 loads at http://localhost:7860
- [ ] Can load sample documents in Project 3
- [ ] Can ask questions in Project 3

---

## 📚 Next Steps

1. **Customize Projects**
   - Use your own datasets
   - Modify models and parameters
   - Add new features

2. **Deploy to Cloud**
   - Streamlit Cloud (free)
   - Railway.app (free tier)
   - Render.com (free tier)
   - Heroku (free tier deprecated, but alternatives available)

3. **Add CI/CD**
   - GitHub Actions
   - Automated testing
   - Deployment pipelines

4. **Document Your Work**
   - Create blog posts
   - Record demo videos
   - Build portfolio website

---

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review error messages carefully
3. Check Docker logs: `docker-compose logs`
4. Verify all prerequisites are installed
5. Try clearing caches and reinstalling

---

**Happy coding! 🚀**
