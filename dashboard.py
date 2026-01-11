import streamlit as st
import pandas as pd
from backend_core import process_job

st.set_page_config(page_title="Leads Engine", page_icon="⚡", layout="wide")
st.title("⚡ AI Lead Generation Engine")

# --- SESSION STATE MANAGEMENT ---
# This dictionary lives in RAM. It is unique to every user.
# It deletes automatically when the tab is closed.
if "data" not in st.session_state:
    st.session_state.data = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("Targeting")
    role = st.text_input("Job Role", "Founder")
    industry = st.text_input("Industry", "Fintech")
    
    if st.button("🚀 Launch Scraper", type="primary"):
        # CLEAR previous results automatically on new search
        st.session_state.data = [] 
        
        with st.spinner(f"Hunting {role}s in {industry}..."):
            # Get fresh data from backend
            raw_results = process_job(role, industry)
            st.session_state.data = raw_results
            
        st.success(f"Found {len(raw_results)} leads!")

# --- MAIN DISPLAY ---
st.divider()

if st.session_state.data:
    # Convert list of dicts to DataFrame
    df = pd.DataFrame(st.session_state.data)
    
    # Move Email to front
    cols = ["Name", "Email", "Company", "Role", "Intent", "Status"]
    # Ensure columns exist even if empty
    df = df.reindex(columns=cols)

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Leads", len(df))
    valid_emails = len(df[df["Email"].notnull()])
    col2.metric("Emails Found", valid_emails)
    col3.metric("Success Rate", f"{int((valid_emails/len(df))*100)}%")
    
    # Display Table
    st.dataframe(df, use_container_width=True)
    
    # Download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='leads_export.csv',
        mime='text/csv',
    )
else:
    st.info("No data in current session. Start a search.")