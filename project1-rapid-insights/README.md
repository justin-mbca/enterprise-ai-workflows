# Project 1: Rapid Insights (Streamlit)

A Streamlit app that simulates Snowflake Cortex AI capabilities using open-source tools.

- Sentiment Analysis (TextBlob)
- Time Series Forecast (simple linear fallback; Prophet optional if available)
- SQL Playground with custom AI SQL functions (SQLite UDFs)

## Local Run

```bash
cd project1-rapid-insights
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub (already done)
2. Go to https://share.streamlit.io
3. Create a new app:
   - Repository: justin-mbca/enterprise-ai-workflows
   - Branch: main
   - App file: project1-rapid-insights/app.py
4. Advanced settings (optional but recommended):
   - Python version: 3.11
   - Dependencies file: project1-rapid-insights/requirements.txt
5. Deploy

Notes:
- We intentionally removed Prophet from requirements to avoid build issues. The app will fallback to a simple forecast if Prophet isn’t available.
- If you want Prophet, add it back to requirements and set up the proper build environment (may take longer and occasionally fail on hosted environments).
