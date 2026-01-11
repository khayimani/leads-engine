import streamlit as st
import requests
import pandas as pd
import time

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Leads Sniper", page_icon="🎯")
st.title("🎯 B2B Lead Sniper")

# --- CONTROL PANEL ---
col1, col2 = st.columns(2)
with col1:
    role = st.text_input("Target Role", "Marketing Director")
with col2:
    industry = st.text_input("Target Industry", "SaaS")

if st.button("🚀 Launch Scraper", type="primary"):
    try:
        # Send command to API
        requests.post(f"{API_URL}/start-job", params={"role": role, "industry": industry})
        st.toast(f"Scraping started for {role}...", icon="🤖")
    except requests.exceptions.ConnectionError:
        st.error("🚨 Error: Is api.py running?")

st.divider()

# --- LIVE RESULTS ---
st.subheader("📥 Captured Leads")

if st.button("🔄 Refresh Data"):
    try:
        response = requests.get(f"{API_URL}/leads")
        data = response.json()
        
        if data:
            df = pd.DataFrame(data)
            # Reorder columns for readability
            df = df[['name', 'role', 'company', 'email', 'intent_score', 'url']]
            st.dataframe(
                df, 
                column_config={
                    "url": st.column_config.LinkColumn("LinkedIn Profile"),
                    "email": st.column_config.TextColumn("Email Address", help="Verified by Tomba")
                },
                hide_index=True
            )
        else:
            st.info("Database is empty. Launch a scraper job!")
            
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API.")