import streamlit as st
import pandas as pd
import sqlite3
import time
from backend_core import process_job

# Page Config
st.set_page_config(page_title="Leads Engine", page_icon="⚡", layout="wide")

# Title
st.title("⚡ AI Lead Generation Engine")
st.markdown("### Multithreaded • Google Sniper • Email Crawler")

# Sidebar: Inputs
with st.sidebar:
    st.header("Targeting")
    role = st.text_input("Job Role", "Founder")
    industry = st.text_input("Industry", "Fintech")
    
    if st.button("🚀 Launch Scraper", type="primary"):
        with st.spinner(f"Hunting {role}s in {industry}... (This uses 5 concurrent threads)"):
            # Run the backend function directly
            process_job(role, industry)
        st.success("Job Finished!")

# Main Area: Results
st.divider()

# Auto-refresh logic
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0

def load_data():
    conn = sqlite3.connect("leads_database.db", check_same_thread=False)
    df = pd.read_sql("SELECT name, role, company, email, intent_score, status FROM leads", conn)
    conn.close()
    return df

try:
    df = load_data()
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Leads", len(df))
    col2.metric("Emails Found", len(df[df["email"].notnull()]))
    col3.metric("Hot Leads", len(df[df["intent_score"] == "HOT"]))
    
    # Table
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "email": st.column_config.TextColumn("Email", help="Verified via Google/Crawling"),
            "intent_score": st.column_config.TextColumn("Intent", help="Hiring signals"),
        }
    )
    
    # Download Button
    st.download_button(
        label="📥 Download CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='leads_export.csv',
        mime='text/csv',
    )
    
except Exception as e:
    st.info("Database empty. Run a job to see results.")