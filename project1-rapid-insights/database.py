"""
Database Manager with AI Functions
Simulates SQL-based AI operations similar to Snowflake Cortex
"""

import sqlite3
import pandas as pd
import numpy as np
from textblob import TextBlob
from datetime import datetime, timedelta
from typing import Dict, Any, List
import re


class DatabaseManager:
    """
    Manages SQLite database with custom AI functions
    Simulates Snowflake Cortex AI capabilities
    """
    
    def __init__(self, db_path: str = ":memory:"):
        """Initialize database connection and create sample data"""
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.setup_database()
        self.register_ai_functions()
    
    def setup_database(self):
        """Create sample tables and data"""
        cursor = self.conn.cursor()
        
        # Create sample tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_feedback (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                text TEXT,
                created_at TIMESTAMP,
                category TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                title TEXT,
                original_text TEXT,
                created_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sample_data (
                id INTEGER PRIMARY KEY,
                category TEXT,
                value REAL,
                created_at TIMESTAMP
            )
        """)
        
        # Insert sample data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM customer_feedback")
        if cursor.fetchone()[0] == 0:
            self._insert_sample_data()
        
        self.conn.commit()
    
    def _insert_sample_data(self):
        """Insert sample data for testing"""
        cursor = self.conn.cursor()
        
        # Sample customer feedback
        feedback_samples = [
            (1, "Absolutely love this product! Best purchase ever.", "product"),
            (2, "Terrible experience. Would not recommend.", "service"),
            (3, "It's okay, nothing special.", "product"),
            (4, "Amazing customer service! They helped me immediately.", "service"),
            (5, "Poor quality, not worth the price.", "product"),
            (6, "Exceeded my expectations! Very happy with this.", "product"),
            (7, "Average product, decent price point.", "product"),
            (8, "Customer support was unhelpful and rude.", "service"),
            (9, "Great value for money! Highly recommend.", "product"),
            (10, "Delivery was late but product is good.", "logistics")
        ]
        
        for i, text, category in feedback_samples:
            cursor.execute("""
                INSERT INTO customer_feedback (customer_id, text, created_at, category)
                VALUES (?, ?, ?, ?)
            """, (i, text, datetime.now(), category))
        
        # Sample documents
        doc_samples = [
            ("Q1 Report", "The first quarter showed strong growth across all segments. Revenue increased by 23% year over year. Customer acquisition costs decreased by 15%. Product development team launched three new features. Marketing campaigns exceeded ROI targets by 18%."),
            ("Customer Survey", "Customers indicated high satisfaction with product quality. Main concerns were shipping times and customer support response rates. 85% would recommend to others. Feature requests focused on mobile app improvements and integration capabilities."),
            ("Technical Analysis", "System performance metrics show 99.9% uptime. Response times averaged 120ms. Database queries optimized resulting in 40% faster load times. Security audit passed with zero critical issues. Infrastructure scaling handled peak loads effectively.")
        ]
        
        for title, text in doc_samples:
            cursor.execute("""
                INSERT INTO documents (title, original_text, created_at)
                VALUES (?, ?, ?)
            """, (title, text, datetime.now()))
        
        # Sample analytics data
        categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Toys']
        for i in range(50):
            cursor.execute("""
                INSERT INTO sample_data (category, value, created_at)
                VALUES (?, ?, ?)
            """, (
                np.random.choice(categories),
                np.random.uniform(10, 1000),
                datetime.now() - timedelta(days=np.random.randint(0, 30))
            ))
        
        self.conn.commit()
    
    def register_ai_functions(self):
        """Register custom AI functions for SQL"""
        
        def sentiment_analysis_udf(text: str) -> float:
            """Calculate sentiment score for text"""
            if not text:
                return 0.0
            blob = TextBlob(str(text))
            return float(blob.sentiment.polarity)
        
        def summarize_text_udf(text: str, num_sentences: int = 2) -> str:
            """Summarize text to specified number of sentences"""
            if not text:
                return ""
            
            # Simple extractive summarization
            sentences = re.split(r'[.!?]+', str(text))
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Take first N sentences as summary
            num_sentences = min(num_sentences, len(sentences))
            return '. '.join(sentences[:num_sentences]) + '.'
        
        def tenure_days_udf(hire_date: str, term_date: str = None) -> int:
            """Compute tenure in days given ISO date strings (YYYY-MM-DD). If term_date is null/empty, uses today."""
            if not hire_date:
                return 0
            try:
                start = datetime.strptime(hire_date[:10], "%Y-%m-%d")
                end = datetime.strptime(term_date[:10], "%Y-%m-%d") if term_date else datetime.today()
                return max(0, (end - start).days)
            except Exception:
                return 0
        
        def overtime_flag_udf(total_hours: float) -> int:
            """Return 1 if weekly hours exceed 40, else 0."""
            try:
                return 1 if float(total_hours) > 40.0 else 0
            except Exception:
                return 0
        
        # Register functions
        self.conn.create_function("sentiment_analysis", 1, sentiment_analysis_udf)
        self.conn.create_function("summarize_text", 2, summarize_text_udf)
        self.conn.create_function("tenure_days", 2, tenure_days_udf)
        self.conn.create_function("overtime_flag", 1, overtime_flag_udf)
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        Simulates: Snowflake SENTIMENT() function
        """
        blob = TextBlob(text)
        
        return {
            'text': text,
            'sentiment': float(blob.sentiment.polarity),
            'subjectivity': float(blob.sentiment.subjectivity),
            'label': 'positive' if blob.sentiment.polarity > 0.1 else 
                    'negative' if blob.sentiment.polarity < -0.1 else 'neutral'
        }
    
    def forecast_timeseries(self, df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
        """
        Forecast time series data
        Simulates: Snowflake ML_FORECAST() function
        
        Args:
            df: DataFrame with 'date' and 'value' columns
            periods: Number of periods to forecast
        
        Returns:
            DataFrame with forecast results
        """
        try:
            from prophet import Prophet
            
            # Prepare data for Prophet
            prophet_df = df.copy()
            prophet_df.columns = ['ds', 'y']
            
            # Fit model
            model = Prophet(
                daily_seasonality=True,
                yearly_seasonality=False,
                weekly_seasonality=True
            )
            model.fit(prophet_df)
            
            # Make forecast
            future = model.make_future_dataframe(periods=periods)
            prophet_pred = model.predict(future)
            
            # Return only forecast period
            forecast_df = prophet_pred.tail(periods)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
            forecast_df.columns = ['date', 'forecast', 'lower_bound', 'upper_bound']
            
            return forecast_df.reset_index(drop=True)
            
        except ImportError:
            # Fallback to simple linear regression if Prophet not installed
            return self._simple_forecast(df, periods)

    def forecast_timeseries_monthly(self, df: pd.DataFrame, months: int = 6) -> pd.DataFrame:
        """Lightweight monthly forecast tuned for visuals:
        - Uses recent momentum (median of last diffs) to extend from last observed value
        - Avoids mean-reversion look of global regression on short windows
        - Returns monthly horizon with simple ±1.96*std(diffs) bounds
        """
        series = df.copy()
        series['date'] = pd.to_datetime(series['date'])
        series = series.sort_values('date')
        y = series['value'].astype(float).values
        n = len(y)

        # Edge cases
        if n == 0:
            return pd.DataFrame({
                'date': pd.to_datetime([]),
                'forecast': [],
                'lower_bound': [],
                'upper_bound': []
            })
        if n == 1:
            last = float(y[-1])
            last_month = series['date'].iloc[-1]
            out_dates = [last_month + pd.DateOffset(months=i+1) for i in range(months)]
            return pd.DataFrame({
                'date': pd.to_datetime([d.strftime('%Y-%m-28') for d in out_dates]),
                'forecast': [last]*months,
                'lower_bound': [last*0.9]*months,
                'upper_bound': [last*1.1]*months,
            })

        # Momentum-based slope from recent changes
        window = int(min(6, n-1))
        recent = y[-(window+1):]
        diffs = np.diff(recent)
        slope = float(np.median(diffs))  # robust to outliers on short series
        last_val = float(y[-1])
        std = float(np.std(diffs)) if diffs.size > 1 else float(np.std(y))

        # Build monthly horizon starting from last observed month
        last_month = series['date'].iloc[-1]
        out_rows = []
        level = last_val
        for i in range(months):
            level = level + slope
            month = (last_month + pd.DateOffset(months=i+1)).strftime('%Y-%m-28')
            out_rows.append((month, level, level - 1.96*std, level + 1.96*std))

        out = pd.DataFrame(out_rows, columns=['date','forecast','lower_bound','upper_bound'])
        out['date'] = pd.to_datetime(out['date'])
        return out
    
    def _simple_forecast(self, df: pd.DataFrame, periods: int) -> pd.DataFrame:
        """Simple linear forecast fallback"""
        # Calculate linear trend (ensure 1D arrays to avoid broadcasting bugs)
        X = np.arange(len(df), dtype=float)  # shape (n,)
        y = df['value'].values.astype(float)

        # Simple linear regression (least squares)
        X_mean = X.mean()
        y_mean = y.mean()
        # Covariance(X, y) / Variance(X)
        numerator = ((X - X_mean) * (y - y_mean)).sum()
        denominator = ((X - X_mean) ** 2).sum()
        slope = (numerator / denominator) if denominator != 0 else 0.0

        # If slope numerically ~0, use recent momentum (median of last diffs)
        if abs(slope) < 1e-9 and len(y) >= 2:
            diffs = np.diff(y[-min(7, len(y)):])
            if diffs.size > 0:
                slope = float(np.median(diffs))

        # Calibrate intercept so the line passes near the last observed value
        y_last = float(y[-1])
        intercept = y_last - slope * (len(df) - 1)
        
        # Generate forecast
        last_date = df['date'].iloc[-1]
        forecast_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        forecast_X = np.arange(len(df), len(df) + periods, dtype=float)
        forecast_y = slope * forecast_X + intercept
        
        # Use volatility of recent changes for bounds
        diffs = np.diff(y)
        std_dev = float(np.std(diffs)) if diffs.size > 0 else float(np.std(y))
        
        return pd.DataFrame({
            'date': forecast_dates,
            'forecast': forecast_y,
            'lower_bound': forecast_y - 1.96 * std_dev,
            'upper_bound': forecast_y + 1.96 * std_dev
        })
    
    def execute_sql(self, query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame
        
        Args:
            query: SQL query string
        
        Returns:
            DataFrame with query results
        """
        return pd.read_sql_query(query, self.conn)

    # ===================== HR/Payroll Helpers =====================
    def seed_hr_data(self):
        """Create and populate HR-focused tables for demos (employees, payroll, survey feedback)."""
        cursor = self.conn.cursor()
        # Employees
        cursor.execute(
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
        # Payroll time series (monthly totals)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS hr_payroll_timeseries (
                id INTEGER PRIMARY KEY,
                month TEXT,
                payroll_amount REAL
            )
            """
        )
        # HR survey feedback
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS hr_survey_feedback (
                id INTEGER PRIMARY KEY,
                department TEXT,
                text TEXT,
                created_at TEXT
            )
            """
        )
        
        # Only seed if empty
        cursor.execute("SELECT COUNT(*) FROM hr_employees")
        if cursor.fetchone()[0] == 0:
            departments = ["Engineering", "Sales", "HR", "Finance", "Support"]
            base_date = datetime.today() - timedelta(days=365*3)
            rows = []
            for i in range(1, 51):
                dept = np.random.choice(departments)
                hire = base_date + timedelta(days=int(np.random.uniform(0, 365*3)))
                term = None if np.random.rand() > 0.15 else hire + timedelta(days=int(np.random.uniform(120, 900)))
                salary = float(np.random.normal(90000, 20000))
                hours = float(np.random.normal(40, 5))
                rows.append((i, f"Emp{i}", "Test", dept, hire.strftime("%Y-%m-%d"), term.strftime("%Y-%m-%d") if term else None, max(45000.0, salary), max(30.0, hours)))
            cursor.executemany(
                """
                INSERT INTO hr_employees (employee_id, first_name, last_name, department, hire_date, term_date, salary, avg_week_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows
            )
        
        cursor.execute("SELECT COUNT(*) FROM hr_payroll_timeseries")
        if cursor.fetchone()[0] == 0:
            # Generate last 18 months of payroll totals
            months = pd.date_range(end=datetime.today(), periods=18, freq='M')
            base = 500000.0
            data = []
            for m in months:
                seasonal = 25000.0 * np.sin(2 * np.pi * (m.month) / 12.0)
                trend = 4000.0 * (months.get_loc(m))
                noise = np.random.normal(0, 15000)
                amt = base + seasonal + trend + noise
                data.append((m.strftime("%Y-%m-28"), float(max(300000.0, amt))))
            cursor.executemany(
                "INSERT INTO hr_payroll_timeseries (month, payroll_amount) VALUES (?, ?)",
                data
            )
        
        cursor.execute("SELECT COUNT(*) FROM hr_survey_feedback")
        if cursor.fetchone()[0] == 0:
            samples = [
                ("Engineering", "I appreciate the flexible hours and supportive team."),
                ("Engineering", "Tech debt is high; sprint planning could improve."),
                ("Sales", "Quarterly targets feel aggressive but achievable."),
                ("Sales", "CRM updates are slow and affect productivity."),
                ("HR", "Onboarding was smooth and well-structured."),
                ("Finance", "We need more automation in reconciliation."),
                ("Support", "Ticket volume is high; need better tooling."),
                ("Support", "Customers are happier after recent changes!")
            ]
            now = datetime.now()
            cursor.executemany(
                "INSERT INTO hr_survey_feedback (department, text, created_at) VALUES (?, ?, ?)",
                [(dept, txt, (now - timedelta(days=int(np.random.uniform(0, 120)))).strftime("%Y-%m-%d %H:%M:%S")) for dept, txt in samples]
            )
        
        self.conn.commit()

    def get_hr_payroll_series(self) -> pd.DataFrame:
        """Return payroll time series as DataFrame with columns ['date','value'] for forecasting."""
        df = pd.read_sql_query("SELECT month as date, payroll_amount as value FROM hr_payroll_timeseries ORDER BY month", self.conn)
        # Ensure datetime type
        df['date'] = pd.to_datetime(df['date'].astype(str).str[:10])
        return df
    
    def close(self):
        """Close database connection"""
        self.conn.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.close()
        except sqlite3.Error:
            pass


# Example usage for testing
if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager()
    
    # Test sentiment analysis
    print("=== Sentiment Analysis Test ===")
    result = db.analyze_sentiment("This product is absolutely amazing!")
    print(f"Sentiment: {result['sentiment']:.3f} ({result['label']})")
    
    # Test SQL with AI functions
    print("\n=== SQL with AI Functions Test ===")
    sql_query = """
        SELECT 
            text,
            sentiment_analysis(text) as sentiment_score,
            CASE 
                WHEN sentiment_analysis(text) > 0.1 THEN 'Positive'
                WHEN sentiment_analysis(text) < -0.1 THEN 'Negative'
                ELSE 'Neutral'
            END as sentiment_label
        FROM customer_feedback
        LIMIT 5
    """
    results = db.execute_sql(sql_query)
    print(results)
    
    # Test forecasting
    print("\n=== Forecasting Test ===")
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    values = 100 + 2 * np.arange(90) + 20 * np.sin(2 * np.pi * np.arange(90) / 30)
    test_df = pd.DataFrame({'date': dates, 'value': values})
    
    forecast = db.forecast_timeseries(test_df, periods=14)
    print(forecast.head())
    
    print("\n✅ All tests completed successfully!")
