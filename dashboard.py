import streamlit as st
import pandas as pd
from backend_core import process_job

st.set_page_config(page_title="Leads Engine", page_icon="⚡", layout="wide")

if "data" not in st.session_state:
    st.session_state.data = []

st.title("⚡ AI Lead Generation Engine")

with st.sidebar:
    st.header("Search")
    role = st.text_input("Role", "Founder")
    industry = st.text_input("Industry", "Fintech")
    if st.button("🚀 Launch Scraper", type="primary"):
        with st.spinner("Hunting..."):
            st.session_state.data = process_job(role, industry)

if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    # Reorder columns for importance
    cols = ["Name", "Email", "Company", "Role", "Intent", "Status"]
    df = df[cols]
    
    st.metric("Success Rate", f"{int((df['Email'].count()/len(df))*100)}%")
    st.dataframe(df, use_container_width=True)
    
    st.download_button("📥 Download", df.to_csv(index=False), "leads.csv")
else:
    st.info("No leads found. Check your targeting.")