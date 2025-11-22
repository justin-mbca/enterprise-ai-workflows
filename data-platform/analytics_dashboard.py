"""
Analytics Dashboard - Visualize dbt Mart Metrics

Consumes data from dbt marts to show business intelligence metrics:
- HR policy features (PTO accrual, overtime mentions)
- Arbitration timelines (filing deadlines)
- Document index statistics

Run: streamlit run analytics_dashboard.py
"""
import streamlit as st
import duckdb
import pandas as pd
import os
from pathlib import Path

# Path to DuckDB warehouse
DUCKDB_PATH = Path(__file__).parent / "dbt" / "warehouse" / "data.duckdb"

st.set_page_config(
    page_title="Data Platform Analytics",
    page_icon="📊",
    layout="wide"
)

@st.cache_resource
def get_connection():
    """Get cached DuckDB connection"""
    if not DUCKDB_PATH.exists():
        st.error(f"❌ DuckDB file not found at {DUCKDB_PATH}")
        st.info("Run `cd dbt && dbt seed && dbt run` first")
        st.stop()
    return duckdb.connect(str(DUCKDB_PATH), read_only=True)

def run_query(sql: str) -> pd.DataFrame:
    """Execute SQL and return DataFrame"""
    con = get_connection()
    return con.execute(sql).df()

# Header
st.title("📊 Data Platform Analytics")
st.markdown("**Real-time metrics from dbt marts**")
st.divider()

# Check dbt run status
try:
    tables = run_query("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema LIKE 'main%'")
    mart_tables = tables[tables['table_schema'] == 'main_marts']['table_name'].tolist()
    
    if not mart_tables:
        st.warning("⚠️ No mart tables found. Run `dbt run` to build models.")
        st.stop()
except Exception as e:
    st.error(f"❌ Error connecting to DuckDB: {e}")
    st.stop()

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "👔 HR Policies", "⚖️ Arbitration", "📚 Document Index"])

# ==========================
# TAB 1: Overview
# ==========================
with tab1:
    st.header("Overview Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_docs = run_query("SELECT COUNT(*) as cnt FROM main_marts.document_index")['cnt'][0]
        st.metric("Total Documents", total_docs)
    
    with col2:
        hr_policies = run_query("SELECT COUNT(*) as cnt FROM main_marts.hr_policy_features")['cnt'][0]
        st.metric("HR Policies", hr_policies)
    
    with col3:
        arb_cases = run_query("SELECT COUNT(*) as cnt FROM main_marts.arbitration_timelines")['cnt'][0]
        st.metric("Arbitration Docs", arb_cases)
    
    st.divider()
    
    # Document distribution by domain
    st.subheader("Document Distribution by Domain")
    domain_dist = run_query("""
        SELECT domain, COUNT(*) as count
        FROM main_marts.document_index
        GROUP BY domain
        ORDER BY count DESC
    """)
    
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        st.bar_chart(domain_dist.set_index('domain'))
    with col_table:
        st.dataframe(domain_dist, use_container_width=True, hide_index=True)

# ==========================
# TAB 2: HR Policies
# ==========================
with tab2:
    st.header("👔 HR Policy Features")
    
    hr_features = run_query("""
        SELECT 
            policy_id,
            category,
            accrual_days_per_month,
            mentions_overtime,
            mentions_payroll_cycle
        FROM main_marts.hr_policy_features
        ORDER BY policy_id
    """)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        pto_count = hr_features[hr_features['accrual_days_per_month'].notna()].shape[0]
        st.metric("PTO Policies", pto_count)
    with col2:
        overtime_count = hr_features['mentions_overtime'].sum()
        st.metric("Mention Overtime", overtime_count)
    with col3:
        payroll_count = hr_features['mentions_payroll_cycle'].sum()
        st.metric("Mention Payroll Cycle", payroll_count)
    
    st.divider()
    
    # Policy breakdown
    st.subheader("Policy Category Breakdown")
    category_dist = run_query("""
        SELECT category, COUNT(*) as count
        FROM main_marts.hr_policy_features
        GROUP BY category
        ORDER BY count DESC
    """)
    st.bar_chart(category_dist.set_index('category'))
    
    st.divider()
    
    # Full table
    st.subheader("Policy Features Detail")
    st.dataframe(
        hr_features,
        use_container_width=True,
        hide_index=True,
        column_config={
            "accrual_days_per_month": st.column_config.NumberColumn(
                "PTO Accrual (days/month)",
                format="%.2f"
            ),
            "mentions_overtime": st.column_config.CheckboxColumn("Overtime?"),
            "mentions_payroll_cycle": st.column_config.CheckboxColumn("Payroll Cycle?")
        }
    )

# ==========================
# TAB 3: Arbitration
# ==========================
with tab3:
    st.header("⚖️ Arbitration Timelines")
    
    arb_data = run_query("""
        SELECT 
            doc_id,
            filing_deadline_days
        FROM main_marts.arbitration_timelines
        WHERE filing_deadline_days IS NOT NULL
        ORDER BY filing_deadline_days
    """)
    
    if arb_data.empty:
        st.info("ℹ️ No deadline information extracted from arbitration documents.")
    else:
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_deadline = arb_data['filing_deadline_days'].mean()
            st.metric("Avg Filing Deadline", f"{avg_deadline:.0f} days")
        with col2:
            min_deadline = arb_data['filing_deadline_days'].min()
            st.metric("Shortest Deadline", f"{min_deadline:.0f} days")
        with col3:
            max_deadline = arb_data['filing_deadline_days'].max()
            st.metric("Longest Deadline", f"{max_deadline:.0f} days")
        
        st.divider()
        
        # Chart
        st.subheader("Filing Deadline Distribution")
        st.bar_chart(arb_data.set_index('doc_id'))
        
        st.divider()
        
        # Table
        st.subheader("Deadline Details")
        st.dataframe(
            arb_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "filing_deadline_days": st.column_config.NumberColumn(
                    "Filing Deadline (days)",
                    format="%d"
                )
            }
        )

# ==========================
# TAB 4: Document Index
# ==========================
with tab4:
    st.header("📚 Document Index (RAG Source)")
    
    doc_index = run_query("""
        SELECT 
            id,
            domain,
            LENGTH(text) as text_length,
            SUBSTRING(text, 1, 100) || '...' as preview
        FROM main_marts.document_index
        ORDER BY domain, id
    """)
    
    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        avg_length = doc_index['text_length'].mean()
        st.metric("Avg Document Length", f"{avg_length:.0f} chars")
    with col2:
        total_chars = doc_index['text_length'].sum()
        st.metric("Total Corpus Size", f"{total_chars:,} chars")
    
    st.divider()
    
    # Filter by domain
    st.subheader("Filter by Domain")
    domains = ['All'] + sorted(doc_index['domain'].unique().tolist())
    selected_domain = st.selectbox("Select Domain", domains)
    
    if selected_domain != 'All':
        filtered_docs = doc_index[doc_index['domain'] == selected_domain]
    else:
        filtered_docs = doc_index
    
    st.dataframe(
        filtered_docs,
        use_container_width=True,
        hide_index=True,
        column_config={
            "text_length": st.column_config.NumberColumn(
                "Length (chars)",
                format="%d"
            ),
            "preview": st.column_config.TextColumn(
                "Preview",
                width="large"
            )
        }
    )
    
    # Export option
    st.divider()
    st.subheader("Export Data")
    col_csv, col_json = st.columns(2)
    with col_csv:
        csv = filtered_docs.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="document_index.csv",
            mime="text/csv"
        )
    with col_json:
        json = filtered_docs.to_json(orient='records', indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json,
            file_name="document_index.json",
            mime="application/json"
        )

# Footer
st.divider()
st.caption("**Data Platform Analytics** | Powered by dbt + DuckDB + Streamlit")
st.caption(f"📂 Data source: `{DUCKDB_PATH}`")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_resource.clear()
    st.rerun()
