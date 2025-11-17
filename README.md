# 🚀 Enterprise AI Workflows - Free Implementation Guide

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
**Tech Stack:** Python, SQLite, Streamlit, TextBlob, Prophet  
**Features:**
- SQL-based sentiment analysis
- Time series forecasting
- Interactive analytics dashboard
- Real-time data visualization

**Run it:**
```bash
cd project1-rapid-insights
streamlit run app.py
```

Live app: https://enterprise-ai-workflows-d3ds3rasntycg5bwaqru5a.streamlit.app

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
- MLflow UI: https://glorious-rotary-phone-g64w6j547wcwjpq-5000.app.github.dev
- Model API: https://glorious-rotary-phone-g64w6j547wcwjpq-8000.app.github.dev/docs
- Jupyter Lab: https://glorious-rotary-phone-g64w6j547wcwjpq-8888.app.github.dev
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
