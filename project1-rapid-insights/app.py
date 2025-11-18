"""
Rapid Insights Workflow - Streamlit Dashboard
Simulates Snowflake Cortex AI capabilities using open-source tools
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseManager
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Enterprise Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize database
# Version marker to force cache invalidation on code updates
DB_VERSION = "v2.0_forecast_fix"

@st.cache_resource
def init_database(version: str = DB_VERSION):
    return DatabaseManager()

db = init_database()

# Fallback seeding in case the deployed DatabaseManager is outdated
def _seed_hr_data_fallback(db_obj: DatabaseManager):
    """Create minimal HR tables and seed a few rows if DatabaseManager lacks seed_hr_data()."""
    try:
        conn = getattr(db_obj, 'conn', None)
        if conn is None:
            return
        cur = conn.cursor()
        # Create tables if not exist
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS hr_employees (
                employee_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                department TEXT,
                hire_date TEXT,
                term_date TEXT,
                salary REAL,
                avg_week_hours REAL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS hr_payroll_timeseries (
                id INTEGER PRIMARY KEY,
                month TEXT,
                payroll_amount REAL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS hr_survey_feedback (
                id INTEGER PRIMARY KEY,
                department TEXT,
                text TEXT,
                created_at TEXT
            )
            """
        )
        # Seed small sample if empty
        cur.execute("SELECT COUNT(*) FROM hr_employees")
        if cur.fetchone()[0] == 0:
            sample_emps = [
                (1, "Alex", "Doe", "Engineering", "2023-01-15", None, 110000.0, 42.0),
                (2, "Sam", "Lee", "Sales", "2022-06-01", None, 85000.0, 38.0),
                (3, "Jamie", "Patel", "HR", "2021-09-10", None, 78000.0, 40.0),
            ]
            cur.executemany(
                """
                INSERT INTO hr_employees (employee_id, first_name, last_name, department, hire_date, term_date, salary, avg_week_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                sample_emps,
            )
        cur.execute("SELECT COUNT(*) FROM hr_payroll_timeseries")
        if cur.fetchone()[0] == 0:
            months = pd.date_range(end=datetime.now(), periods=6, freq='M')
            base = 500000.0
            data = []
            for i, m in enumerate(months):
                amt = base + 10000 * i + np.random.normal(0, 10000)
                data.append((m.strftime("%Y-%m-28"), float(max(300000.0, amt))))
            cur.executemany(
                "INSERT INTO hr_payroll_timeseries (month, payroll_amount) VALUES (?, ?)",
                data,
            )
        cur.execute("SELECT COUNT(*) FROM hr_survey_feedback")
        if cur.fetchone()[0] == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            feedback = [
                ("Engineering", "I appreciate flexible hours and supportive team.", now),
                ("Sales", "Quarterly targets are aggressive but motivating.", now),
                ("HR", "Onboarding process is smooth.", now),
            ]
            cur.executemany(
                "INSERT INTO hr_survey_feedback (department, text, created_at) VALUES (?, ?, ?)",
                feedback,
            )
        conn.commit()
    except Exception:
        # Silent fallback; actual DatabaseManager.seed_hr_data should handle the full dataset
        pass


def _get_hr_payroll_series_fallback(db_obj: DatabaseManager) -> pd.DataFrame:
    """Read payroll time series from SQLite directly and return ['date','value'].
    If the table is missing/empty, seed minimal data and retry.
    """
    conn = getattr(db_obj, 'conn', None)
    if conn is None:
        # Return empty DataFrame with expected columns
        return pd.DataFrame({"date": pd.to_datetime([]), "value": []})
    try:
        ts_df_local = pd.read_sql_query(
            "SELECT month as date, payroll_amount as value FROM hr_payroll_timeseries ORDER BY month",
            conn,
        )
        if ts_df_local.empty:
            _seed_hr_data_fallback(db_obj)
            ts_df_local = pd.read_sql_query(
                "SELECT month as date, payroll_amount as value FROM hr_payroll_timeseries ORDER BY month",
                conn,
            )
        ts_df_local['date'] = pd.to_datetime(ts_df_local['date'].astype(str).str[:10])
        return ts_df_local
    except Exception:
        # Ensure tables exist then retry once
        _seed_hr_data_fallback(db_obj)
        try:
            ts_df_local = pd.read_sql_query(
                "SELECT month as date, payroll_amount as value FROM hr_payroll_timeseries ORDER BY month",
                conn,
            )
            ts_df_local['date'] = pd.to_datetime(ts_df_local['date'].astype(str).str[:10])
            return ts_df_local
        except Exception:
            return pd.DataFrame({"date": pd.to_datetime([]), "value": []})

# Sidebar
st.sidebar.title("🚀 Rapid Insights")
st.sidebar.markdown("**Simulates:** Snowflake Cortex AI")
st.sidebar.markdown("**Tech Stack:** Python, SQLite, Streamlit")

page = st.sidebar.selectbox(
    "Select Analysis",
    ["📊 Overview", "💬 Sentiment Analysis", "📈 Forecasting", "🔍 SQL Playground", "👥 HR Analytics"]
)

# Main title
st.title("Enterprise Analytics Dashboard")
st.markdown("*Powered by open-source AI tools*")

# ============================================================================
# PAGE 1: OVERVIEW
# ============================================================================
if page == "📊 Overview":
    st.header("Dashboard Overview")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", "10,247", "+1,234")
    with col2:
        st.metric("Avg Sentiment", "0.65", "+0.05")
    with col3:
        st.metric("Forecast Accuracy", "94.2%", "+2.1%")
    with col4:
        st.metric("Active Users", "3,456", "+234")
    
    # Sample data visualization
    st.subheader("Sample Customer Feedback Analysis")
    
    # Generate sample data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    sample_data = pd.DataFrame({
        'Date': dates,
        'Positive': np.random.randint(50, 150, 30),
        'Neutral': np.random.randint(20, 80, 30),
        'Negative': np.random.randint(10, 50, 30)
    })
    
    fig = px.area(
        sample_data,
        x='Date',
        y=['Positive', 'Neutral', 'Negative'],
        title='Sentiment Trends Over Time',
        labels={'value': 'Count', 'variable': 'Sentiment'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.subheader("🎯 Key Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("✅ Customer satisfaction trending upward")
        st.info("ℹ️ Product mentions increased 23% this month")
    
    with col2:
        st.warning("⚠️ Response time needs improvement")
        st.success("✅ Sales forecast meets targets")

# ============================================================================
# PAGE 2: SENTIMENT ANALYSIS
# ============================================================================
elif page == "💬 Sentiment Analysis":
    st.header("Sentiment Analysis")
    st.markdown("*Simulates Snowflake Cortex `SENTIMENT()` function*")
    
    # Input section
    st.subheader("Analyze Text")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        text_input = st.text_area(
            "Enter text to analyze:",
            placeholder="Type or paste customer feedback, reviews, or any text...",
            height=150
        )
    
    with col2:
        st.markdown("#### Quick Examples")
        if st.button("😊 Positive Example"):
            text_input = "This product is absolutely amazing! Best purchase I've made this year. Highly recommend!"
            st.rerun()
        if st.button("😐 Neutral Example"):
            text_input = "The product arrived on time. It works as described in the specifications."
            st.rerun()
        if st.button("😞 Negative Example"):
            text_input = "Very disappointed with this purchase. Poor quality and doesn't work as advertised."
            st.rerun()
    
    if st.button("🔍 Analyze Sentiment", type="primary"):
        if text_input:
            with st.spinner("Analyzing..."):
                result = db.analyze_sentiment(text_input)
                
                # Display results
                st.subheader("Analysis Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    sentiment_emoji = "😊" if result['sentiment'] > 0 else "😞" if result['sentiment'] < 0 else "😐"
                    st.metric("Sentiment Score", f"{result['sentiment']:.3f} {sentiment_emoji}")
                
                with col2:
                    st.metric("Subjectivity", f"{result['subjectivity']:.3f}")
                
                with col3:
                    label = "Positive" if result['sentiment'] > 0.1 else "Negative" if result['sentiment'] < -0.1 else "Neutral"
                    st.metric("Classification", label)
                
                # Gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=result['sentiment'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Sentiment Score"},
                    delta={'reference': 0},
                    gauge={
                        'axis': {'range': [-1, 1]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [-1, -0.3], 'color': "lightcoral"},
                            {'range': [-0.3, 0.3], 'color': "lightyellow"},
                            {'range': [0.3, 1], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 0
                        }
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please enter some text to analyze")
    
    # Batch analysis
    st.markdown("---")
    st.subheader("Batch Analysis")
    
    uploaded_file = st.file_uploader("Upload CSV file with 'text' column", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        if 'text' in df.columns:
            st.info(f"📄 Loaded {len(df)} records")
            
            if st.button("Analyze All", type="primary"):
                with st.spinner("Processing batch..."):
                    results = []
                    progress_bar = st.progress(0)
                    
                    for idx, text in enumerate(df['text']):
                        result = db.analyze_sentiment(str(text))
                        results.append(result['sentiment'])
                        progress_bar.progress((idx + 1) / len(df))
                    
                    df['sentiment_score'] = results
                    df['sentiment_label'] = df['sentiment_score'].apply(
                        lambda x: 'Positive' if x > 0.1 else 'Negative' if x < -0.1 else 'Neutral'
                    )
                    
                    st.success("✅ Analysis complete!")
                    
                    # Show results
                    st.dataframe(df.head(10))
                    
                    # Distribution chart
                    fig = px.histogram(
                        df,
                        x='sentiment_score',
                        nbins=50,
                        title='Sentiment Distribution',
                        labels={'sentiment_score': 'Sentiment Score'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Download results
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Results",
                        csv,
                        "sentiment_analysis_results.csv",
                        "text/csv"
                    )
        else:
            st.error("CSV must contain a 'text' column")

# ============================================================================
# PAGE 3: FORECASTING
# ============================================================================
elif page == "📈 Forecasting":
    st.header("Time Series Forecasting")
    st.markdown("*Simulates Snowflake `ML_FORECAST()` function*")
    
    # Data generation options
    st.subheader("Generate Sample Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        periods = st.slider("Historical periods", 30, 365, 180)
    with col2:
        forecast_periods = st.slider("Forecast periods", 7, 90, 30)
    with col3:
        trend = st.selectbox("Trend", ["Upward", "Downward", "Seasonal"])
    
    if st.button("🎲 Generate & Forecast", type="primary"):
        with st.spinner("Generating forecast..."):
            # Generate sample time series
            dates = pd.date_range(end=datetime.now(), periods=periods, freq='D')
            
            # Create data with trend and seasonality
            t = np.arange(periods)
            if trend == "Upward":
                y = 100 + 2 * t + 20 * np.sin(2 * np.pi * t / 30) + np.random.randn(periods) * 5
            elif trend == "Downward":
                y = 200 - 1 * t + 20 * np.sin(2 * np.pi * t / 30) + np.random.randn(periods) * 5
            else:
                y = 150 + 30 * np.sin(2 * np.pi * t / 30) + np.random.randn(periods) * 5
            
            df = pd.DataFrame({
                'date': dates,
                'value': y
            })
            
            # Make forecast
            forecast_df = db.forecast_timeseries(df, forecast_periods)
            
            # Plot results
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['value'],
                mode='lines',
                name='Historical',
                line=dict(color='blue')
            ))
            
            # Forecast
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['forecast'],
                mode='lines',
                name='Forecast',
                line=dict(color='red', dash='dash')
            ))
            
            # Confidence interval
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['upper_bound'],
                mode='lines',
                name='Upper Bound',
                line=dict(width=0),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['lower_bound'],
                mode='lines',
                name='Lower Bound',
                line=dict(width=0),
                fillcolor='rgba(255, 0, 0, 0.2)',
                fill='tonexty',
                showlegend=True
            ))
            
            fig.update_layout(
                title='Time Series Forecast',
                xaxis_title='Date',
                yaxis_title='Value',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast metrics
            st.subheader("📊 Forecast Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Forecast Mean", f"{forecast_df['forecast'].mean():.2f}")
            with col2:
                st.metric("Forecast Trend", f"{(forecast_df['forecast'].iloc[-1] - forecast_df['forecast'].iloc[0]):.2f}")
            with col3:
                st.metric("Confidence Range", f"±{forecast_df['upper_bound'].iloc[0] - forecast_df['forecast'].iloc[0]:.2f}")
            with col4:
                trend_pct = ((forecast_df['forecast'].iloc[-1] / df['value'].iloc[-1]) - 1) * 100
                st.metric("Growth %", f"{trend_pct:.1f}%")
            
            # Show data table
            st.subheader("📋 Forecast Data")
            st.dataframe(forecast_df)
            
            # Download
            csv = forecast_df.to_csv(index=False)
            st.download_button(
                "📥 Download Forecast",
                csv,
                "forecast_results.csv",
                "text/csv"
            )

# ============================================================================
# PAGE 4: SQL PLAYGROUND
# ============================================================================
elif page == "🔍 SQL Playground":
    st.header("SQL Playground with AI Functions")
    st.markdown("*Try SQL queries with custom AI functions*")
    
    # Sample queries
    st.subheader("📝 Sample Queries")
    
    sample_queries = {
        "Sentiment Analysis": """
-- Analyze sentiment of customer feedback
SELECT 
    text,
    sentiment_analysis(text) as sentiment_score,
    CASE 
        WHEN sentiment_analysis(text) > 0.1 THEN 'Positive'
        WHEN sentiment_analysis(text) < -0.1 THEN 'Negative'
        ELSE 'Neutral'
    END as sentiment_label
FROM customer_feedback
LIMIT 10;
        """,
        "Summary Generation": """
-- Generate summary of long text
SELECT 
    id,
    original_text,
    summarize_text(original_text, 2) as summary
FROM documents
WHERE LENGTH(original_text) > 100
LIMIT 5;
        """,
        "Simple Analytics": """
-- Basic data analysis
SELECT 
    category,
    COUNT(*) as count,
    AVG(value) as avg_value,
    MAX(value) as max_value
FROM sample_data
GROUP BY category
ORDER BY count DESC;
        """
    }
    
    cols = st.columns(len(sample_queries))
    for idx, (name, query) in enumerate(sample_queries.items()):
        with cols[idx]:
            if st.button(name):
                st.session_state.query = query
    
    # Query editor
    query = st.text_area(
        "Enter SQL Query:",
        value=st.session_state.get('query', ''),
        height=200,
        placeholder="SELECT * FROM table_name LIMIT 10;"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        execute_btn = st.button("▶️ Execute", type="primary")
    with col2:
        st.info("💡 Available AI functions: `sentiment_analysis(text)`, `summarize_text(text, sentences)`")
    
    if execute_btn and query:
        try:
            with st.spinner("Executing query..."):
                result_df = db.execute_sql(query)
                
                st.success(f"✅ Query executed successfully! ({len(result_df)} rows)")
                
                # Display results
                st.dataframe(result_df, use_container_width=True)
                
                # Quick stats
                if len(result_df) > 0:
                    st.subheader("📊 Quick Stats")
                    st.write(f"Rows: {len(result_df)} | Columns: {len(result_df.columns)}")
                    
                    # Download
                    csv = result_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Results",
                        csv,
                        "query_results.csv",
                        "text/csv"
                    )
        except Exception as e:
            st.error(f"❌ Error executing query: {str(e)}")
    
    # Documentation
    st.markdown("---")
    st.subheader("📚 Available AI Functions")
    
    with st.expander("sentiment_analysis(text)"):
        st.code("""
-- Returns sentiment score between -1 (negative) and 1 (positive)
SELECT sentiment_analysis('This is amazing!') as score;
-- Result: 0.875
        """, language="sql")
    
    with st.expander("summarize_text(text, num_sentences)"):
        st.code("""
-- Summarizes text to specified number of sentences
SELECT summarize_text('Long text here...', 2) as summary;
-- Result: First sentence. Second sentence.
        """, language="sql")

# ============================================================================
# PAGE 5: HR ANALYTICS
# ============================================================================
elif page == "👥 HR Analytics":
    st.header("HR & Payroll Analytics")
    st.markdown("*Workforce planning, payroll forecasting, and employee feedback sentiment*")

    # Seed data
    st.subheader("Setup")
    if st.button("📥 Load Sample HR Data", type="primary"):
        with st.spinner("Seeding HR tables..."):
            try:
                if hasattr(db, "seed_hr_data"):
                    db.seed_hr_data()
                else:
                    _seed_hr_data_fallback(db)
            except AttributeError:
                _seed_hr_data_fallback(db)
        st.success("✅ HR tables seeded: employees, payroll_timeseries, survey_feedback")

    st.markdown("---")
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📈 Payroll Forecast (Monthly Totals)")
        forecast_months = st.slider("Forecast months", 1, 12, 6)
        try:
            if hasattr(db, "get_hr_payroll_series"):
                ts_df = db.get_hr_payroll_series()
            else:
                ts_df = _get_hr_payroll_series_fallback(db)
            st.caption(f"Historical periods: {len(ts_df)} months")
            if len(ts_df) > 3:
                with st.spinner("Forecasting payroll totals..."):
                    # Prefer monthly forecast for better visibility on monthly series
                    if hasattr(db, "forecast_timeseries_monthly"):
                        forecast_df = db.forecast_timeseries_monthly(ts_df, forecast_months)
                    else:
                        forecast_df = db.forecast_timeseries(ts_df, forecast_months*30)
                # Plot
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=ts_df['date'], y=ts_df['value'], mode='lines', name='Historical', line=dict(color='blue')))
                fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['forecast'], mode='lines', name='Forecast', line=dict(color='red', dash='dash')))
                fig.update_layout(title='Monthly Payroll Total (Historical + Forecast)', xaxis_title='Date', yaxis_title='Amount', hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)
                # Metrics
                colm1, colm2 = st.columns(2)
                with colm1:
                    st.metric("Forecast Mean", f"{forecast_df['forecast'].mean():,.0f}")
                with colm2:
                    st.metric("Last Forecast", f"{forecast_df['forecast'].iloc[-1]:,.0f}")
            else:
                st.info("Load sample HR data to view payroll time series.")
        except Exception as e:
            st.warning(f"Unable to load payroll series: {e}")

    with col_right:
        st.subheader("💬 Sentiment by Department")
        try:
            sentiment_df = db.execute_sql(
                """
                SELECT department,
                       AVG(sentiment_analysis(text)) AS avg_sentiment,
                       COUNT(*) AS n
                FROM hr_survey_feedback
                GROUP BY department
                ORDER BY department
                """
            )
            if len(sentiment_df) > 0:
                fig2 = px.bar(sentiment_df, x='department', y='avg_sentiment', title='Average Sentiment by Department', color='department')
                st.plotly_chart(fig2, use_container_width=True)
                st.dataframe(sentiment_df)
            else:
                st.info("Load sample HR data to analyze survey sentiment.")
        except Exception as e:
            st.warning(f"Unable to compute sentiment: {e}")

    st.markdown("---")
    st.subheader("🧪 Sample HR SQL (features in SQL)")
    with st.expander("Employee tenure in days (tenure_days)"):
        st.code(
            """
-- Compute tenure days and status
SELECT employee_id, department, hire_date, term_date,
       tenure_days(hire_date, term_date) AS tenure_days,
       CASE WHEN term_date IS NULL THEN 'Active' ELSE 'Terminated' END AS status
FROM hr_employees
LIMIT 10;
            """,
            language="sql",
        )
    with st.expander("Overtime flag (overtime_flag)"):
        st.code(
            """
-- Flag overtime based on average weekly hours
SELECT employee_id, department, avg_week_hours,
       overtime_flag(avg_week_hours) AS has_overtime
FROM hr_employees
ORDER BY avg_week_hours DESC
LIMIT 10;
            """,
            language="sql",
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ using Streamlit, TextBlob, and Prophet</p>
    <p>🎯 <b>Interview Tip:</b> This demonstrates Snowflake Cortex capabilities using open-source alternatives</p>
</div>
""", unsafe_allow_html=True)
