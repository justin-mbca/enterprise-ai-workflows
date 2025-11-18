# 🚀 Enterprise AI Workflows - Free Implementation Guide

## Quick launch

<p>
  <a href="https://enterprise-ai-workflows-d3ds3rasntycg5bwaqru5a.streamlit.app">
    <img alt="Streamlit App" src="https://img.shields.io/badge/Project%201-Streamlit%20App-ff4b4b?logo=streamlit&logoColor=white">
  </a>
  <a href="https://zhangju2023-mlops-pipeline-demo.hf.space/mlflow/">
    <img alt="MLflow UI" src="https://img.shields.io/badge/Project%202-MLflow%20UI-0194E2">
  </a>
  <a href="https://zhangju2023-mlops-pipeline-demo.hf.space/api/docs">
    <img alt="API Docs" src="https://img.shields.io/badge/Project%202-API%20Docs-009688?logo=fastapi&logoColor=white">
  </a>
  <a href="https://zhangju2023-mlops-pipeline-demo.hf.space/api/health">
    <img alt="API Health" src="https://img.shields.io/badge/Project%202-Health-4caf50">
  </a>
  <a href="https://zhangju2023-mlops-pipeline-demo.hf.space/api/predict/example">
    <img alt="Example Prediction" src="https://img.shields.io/badge/Project%202-Example%20Prediction-7c4dff">
  </a>
  <a href="https://huggingface.co/spaces/zhangju2023/document-qa-rag">
    <img alt="RAG App" src="https://img.shields.io/badge/Project%203-RAG%20App-ffcc4d?logo=huggingface&logoColor=black">
  </a>
</p>

> Learn enterprise AI/ML workflows using **100% free and open-source tools**. Perfect for building your portfolio and preparing for interviews!

## 📋 Overview

This repository contains three production-ready projects that demonstrate enterprise AI/ML workflows without expensive licenses:

1. **Rapid Insights Workflow** - SQL-based analytics with AI capabilities
2. **Enterprise MLOps Pipeline** - Complete ML lifecycle management
3. **Document Q&A System** - RAG-based LLM application

## 🎯 What You'll Learn

- **MLOps Best Practices** - Experiment tracking, model registry, deployment
- **Data Analytics** - SQL, Python, real-time dashboards
- **LLM Applications** - RAG pipelines, vector databases, embeddings
- **Cloud Architecture** - Scalable, production-ready patterns
- **DevOps** - Docker, CI/CD, containerization

## 🗂️ Project Structure

```
enterprise-ai-workflows/
├── project1-rapid-insights/        # Snowflake Cortex alternative
│   ├── app.py                      # Streamlit dashboard
│   ├── database.py                 # SQLite with AI functions
│   └── requirements.txt
│
├── project2-mlops-pipeline/        # Azure ML alternative
│   ├── docker-compose.yml          # MLflow + Jupyter + PostgreSQL
│   ├── notebooks/                  # Experiment notebooks
│   ├── models/                     # Model training scripts
│   └── deployment/                 # FastAPI deployment
│
├── project3-document-qa/           # LLM RAG application
│   ├── app.py                      # Gradio interface
│   ├── rag_pipeline.py             # Vector search + LLM
│   └── requirements.txt
│
└── docs/                           # Additional documentation
    ├── setup-guide.md
    ├── interview-prep.md
    └── architecture-decisions.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- Docker Desktop (for Project 2)
- 5GB free disk space

### Installation

```bash
# Clone and enter the directory
cd enterprise-ai-workflows

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# Install dependencies for a specific project
cd project1-rapid-insights
pip install -r requirements.txt
```

## 📊 Project Details

### Project 1: Rapid Insights Workflow
**Simulates:** Snowflake Cortex AI  
**Tech Stack:** Python, SQLite, Streamlit, TextBlob, NumPy  
**Features:**
- 📊 **Advanced Time Series Forecasting**: Intelligent trend detection with recent-window slope calculation and automatic seasonal pattern recognition
- 💬 **SQL-based Sentiment Analysis**: TextBlob integration via SQLite UDFs
- 📝 **Text Summarization**: Extractive summarization accessible through SQL
- 🧑‍💼 **HR & Payroll Analytics**: Sample datasets with payroll forecasting, employee tenure tracking, and overtime detection
- 🎨 **Interactive Dashboard**: Real-time visualizations with Plotly

**Run it:**
```bash
cd project1-rapid-insights
streamlit run app.py
```

**Live app:** https://enterprise-ai-workflows-d3ds3rasntycg5bwaqru5a.streamlit.app

**Key Innovations:**
- Momentum-based forecasting for trending data (captures recent patterns)
- Naive seasonal forecasting for cyclical data (repeats patterns intelligently)
- Smart cache management with version markers for seamless updates

### Project 2: Enterprise MLOps Pipeline
**Simulates:** Azure ML, Dataiku  
**Tech Stack:** MLflow, Docker, PostgreSQL, FastAPI, Scikit-learn  
**Features:**
- Experiment tracking
- Model registry
- Automated retraining
- REST API deployment
- CI/CD pipeline

**Run it:**
```bash
cd project2-mlops-pipeline
docker-compose up -d
# Access MLflow at http://localhost:5000
# Access Jupyter at http://localhost:8888
```

**Live deployments:**

Hugging Face Space (persistent demo):
- MLflow UI: https://zhangju2023-mlops-pipeline-demo.hf.space/mlflow/
- Model API: https://zhangju2023-mlops-pipeline-demo.hf.space/api/docs
 - Health: https://zhangju2023-mlops-pipeline-demo.hf.space/api/health
 - Example prediction: https://zhangju2023-mlops-pipeline-demo.hf.space/api/predict/example

 Notes:
 - Runs in demo mode by default (no external model required)
 - MLflow is auto-seeded with a demo model (customer_churn_model → Production)

GitHub Codespaces (temporary):
- MLflow UI: https://glorious-rotary-phone-g64w6j547wcwjpq-5000.app.github.dev
- Model API: https://glorious-rotary-phone-g64w6j547wcwjpq-8000.app.github.dev/docs
- Jupyter Notebook: https://glorious-rotary-phone-g64w6j547wcwjpq-8888.app.github.dev/lab/tree/notebooks/01_customer_churn_mlops.ipynb
  
  Note: Codespaces URLs are temporary and only reachable while that Codespace is running. After the Codespace auto-sleeps, click Resume in the Codespaces UI and restart services:    ```bash
    bash project2-mlops-pipeline/scripts/start-mlops-nodocker.sh
    ```
  
    If the Codespace is deleted, these URLs will no longer work; open a new Codespace from the quickstart link to spin up a fresh demo.

     Start/Resume the demo (opens a Codespace):
     https://codespaces.new/justin-mbca/enterprise-ai-workflows?quickstart=1
### Project 3: Document Q&A System

[![Open in Hugging Face Spaces](https://img.shields.io/badge/Spaces-Open%20App-blue?logo=huggingface)](https://huggingface.co/spaces/zhangju2023/document-qa-rag)

**Simulates:** Azure OpenAI RAG  
**Tech Stack:** ChromaDB, SentenceTransformers, Hugging Face Transformers  
**Features:**
- Document ingestion
- Vector embeddings
- Semantic search
- Question answering
- Web interface

**Run it:**
```bash
cd project3-document-qa
python app.py
# Access at http://localhost:7860
```

Live app: https://huggingface.co/spaces/zhangju2023/document-qa-rag

## 💰 Cost Breakdown

| Component | Enterprise Tool | Free Alternative | Savings |
|-----------|----------------|------------------|---------|
| Data Warehouse | Snowflake ($2000+/year) | PostgreSQL + SQLite | $2000+ |
| MLOps Platform | Azure ML ($1000+/year) | MLflow + Docker | $1000+ |
| Low-code ML | Dataiku ($50k+/year) | Jupyter + Streamlit | $50k+ |
| LLM API | Azure OpenAI ($100+/month) | Open models (local) | $1200+ |
| **Total** | **$54,200+/year** | **$0** | **$54,200+** |

## 🎯 Interview Talking Points

### How to Discuss These Projects

**For Tool-Specific Questions:**
> "I implemented this using MLflow to master MLOps fundamentals—the concepts of experiment tracking, model versioning, and deployment pipelines transfer directly to Azure ML. I can adapt quickly to your tech stack."

**For Architecture Questions:**
> "I designed this to mirror production patterns: separate data layer, orchestration layer, and serving layer. Here's how I handled [specific challenge]..."

**For Problem-Solving Questions:**
> "When building my RAG pipeline, I optimized vector search performance by [specific solution]. This taught me [learning outcome]."

## 📚 Learning Path

### Week 1-2: Project 1 (Rapid Insights)
- Learn SQL-based analytics
- Implement AI functions
- Build interactive dashboards

### Week 3-4: Project 2 (MLOps)
- Set up experiment tracking
- Implement model lifecycle
- Deploy via REST API

### Week 5-6: Project 3 (Document Q&A)
- Work with embeddings
- Build vector search
- Create LLM application

### Week 7-8: Polish & Deploy
- Add CI/CD pipelines
- Write comprehensive docs
- Deploy to free hosting

## 🔗 Free Resources Used

- **Datasets:** Kaggle, UCI ML Repository
- **Models:** Hugging Face Hub
- **Hosting:** Streamlit Cloud, Railway.app, Render
- **Compute:** Google Colab, Kaggle Notebooks
- **Version Control:** GitHub (free tier)

## 🌟 Next Steps

1. **Start with Project 1** - Easiest to set up and run
2. **Document your learnings** - Keep notes on challenges and solutions
3. **Customize for your domain** - Use data relevant to your target industry
4. **Deploy publicly** - Show working demos in interviews
5. **Write blog posts** - Explain your implementation decisions

## 🌐 Website

Static showcase (GitHub Pages): If Pages is enabled for this repo using the `/docs` folder, visit:
https://justin-mbca.github.io/enterprise-ai-workflows/

This site lists all projects and links to the live demos (Streamlit, Hugging Face Spaces, Codespaces).

## 🤝 Contributing

Have improvements or alternative implementations? PRs welcome!

## 📄 License

MIT License - Free to use for personal and commercial projects

## 💡 Additional Resources

- [Setup Guide](docs/setup-guide.md) - Detailed installation instructions
- [Interview Prep](docs/interview-prep.md) - Common questions and answers
- [Architecture Decisions](docs/architecture-decisions.md) - Why we chose each tool

---

**Remember:** Companies hire problem-solvers, not tool experts. These projects prove you understand the underlying concepts and can build real solutions! 🚀

Built with ❤️ using 100% free and open-source tools.
