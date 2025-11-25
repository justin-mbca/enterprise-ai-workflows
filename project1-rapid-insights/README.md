# Project 1: Rapid Insights (Streamlit)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://enterprise-ai-workflows-d3ds3rasntycg5bwaqru5a.streamlit.app)

Live app: https://enterprise-ai-workflows-d3ds3rasntycg5bwaqru5a.streamlit.app

A Streamlit app that simulates Snowflake Cortex AI capabilities using open-source tools.

## Features

### 📊 Time Series Forecasting
- **Simulates Snowflake `ML_FORECAST()` function**
- Intelligent trend detection:
  - **Upward/Downward trends**: Recent-window slope calculation for accurate momentum-based forecasts
  - **Seasonal patterns**: Automatic pattern detection and naive seasonal forecasting (repeats last cycle)
- Anchored forecasts that start at the last observed value for visual continuity
- Confidence intervals based on historical volatility
- Prophet integration optional (falls back to optimized linear/seasonal methods)

### 💬 Sentiment Analysis
- **Simulates Snowflake `SENTIMENT()` function**
- Uses TextBlob for natural language sentiment scoring
- Available as SQL UDF: `SELECT sentiment_analysis(text_column) FROM table`

### 📝 Text Summarization
- **Simulates Snowflake `SUMMARIZE()` function**
- Extractive summarization using sentence ranking
- Available as SQL UDF: `SELECT summarize_text(text_column) FROM table`

### 🧑‍💼 HR & Payroll Analytics
- Sample HR datasets: employees, payroll timeseries, survey feedback
- Payroll forecasting with monthly trend visualization
- Department sentiment analysis from survey feedback
- Custom SQL UDFs:
  - `tenure_days(hire_date, term_date)` - Calculate employee tenure
  - `overtime_flag(avg_week_hours)` - Flag overtime workers (>40 hrs)
- Interactive SQL playground with HR-specific sample queries

### 🔧 SQL Playground
- Execute custom SQL queries against SQLite database
- Pre-loaded with AI functions as SQLite UDFs
- Sample queries for sentiment analysis, summarization, and HR analytics

## 🚀 New: Prompt Engineering, Data Annotation, RLHF, and Model Feedback

This app now supports advanced human-in-the-loop AI workflows:

### 1. Prompt Engineering
- Edit the prompt template used for sentiment analysis (with `{text}` placeholder)
- See the exact prompt sent to the model for each analysis
- Experiment with prompt wording to observe effects on model output

### 2. Data Annotation
- After each sentiment analysis, label the true sentiment (Positive, Neutral, Negative)
- Annotations are saved to `sentiment_annotations.csv` for future training or evaluation

### 3. Model Performance Feedback
- Provide thumbs up/down feedback on model predictions
- Optionally add comments about model performance
- Feedback is saved to `sentiment_feedback.csv` for RLHF or analysis

### 4. RLHF Data Collection
- All (input, prompt, model output, user label, feedback, comments) are stored
- These CSVs can be used to train reward models or fine-tune LLMs with human feedback (offline, e.g., with Hugging Face TRL)

**Example RLHF Data Row:**
| text | model_sentiment | user_label | feedback | comment | prompt_template |
|------|----------------|------------|----------|---------|----------------|
| ...  | Positive       | Negative   | 👎 No    | "Missed sarcasm" | ... |

**How to Use:**
- Edit the prompt, analyze text, label the result, and submit feedback—all in the Sentiment Analysis page
- Download or process the resulting CSVs for further ML workflows

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

Or open the already deployed app here:

- https://enterprise-ai-workflows-d3ds3rasntycg5bwaqru5a.streamlit.app

## Technical Notes

### Forecasting Implementation
- **Trend forecasting**: Uses recent-window (last 30 points) linear regression for better momentum capture
- **Seasonal forecasting**: Detects pure oscillations and repeats last 60-day cycle pattern
- **Smart fallback**: Automatically selects appropriate method based on data characteristics
- **Prophet optional**: Removed from default requirements to avoid build issues; optimized fallback methods work great for demos

### HR Analytics
- All HR data is sample/synthetic for demonstration purposes
- Uses SQLite UDFs for efficient in-database computation
- Forecasting uses momentum-based monthly projection for cleaner visualizations

### Cache Management
- DatabaseManager cached with `@st.cache_resource` for performance
- Version marker forces cache invalidation on code updates
- Graceful fallback handles cache incompatibilities during deployments
