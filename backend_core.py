import requests
import json
import re
import html
import os
import concurrent.futures
from email_engine import EmailEngine

SERPER_API_KEY = "e3b6016ca8de93b72ee9d85593448539c84160f8"
MAX_WORKERS = 5
engine = EmailEngine(SERPER_API_KEY)

# Database Configuration
# Allow overriding the DB path for production (e.g. using a persistent volume)
DB_NAME = os.getenv("DB_PATH", "leads_database.db")

def scrape_linkedin_leads(role, industry, limit=15):
    url = "https://google.serper.dev/search"
    query = f'site:linkedin.com/in "{role}" "{industry}"'
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    
    try:
        r = requests.post(url, headers=headers, json={"q": query, "num": limit}, timeout=10)
        data = r.json()
    except:
        return []

    leads = []
    for r in data.get("organic", []):
        title = r.get("title", "")
        snippet = html.unescape(r.get("snippet", ""))
        
        clean_title = title.replace(" | LinkedIn", "").replace(" - LinkedIn", "")
        name = clean_title.split(" - ")[0].split(" | ")[0].strip()
        
        # FIXED: More permissive company extraction
        company = "Unknown"
        # Match "at [Company] ·", "at [Company] |", "at [Company] -", or "@ [Company]"
        match = re.search(r"(?:at|@)\s+([^·|\-|]+)", snippet)
        if match:
            company = match.group(1).strip()
        
        if (company == "Unknown") and " - " in clean_title:
            parts = clean_title.split(" - ")
            if len(parts) >= 2: company = parts[-1].strip()

        # FIXED: Append even if company is Unknown to allow EmailEngine to try/fail later
        leads.append({
            "name": name,
            "role": role,
            "company": company,
            "url": r.get("link"),
            "snippet": snippet
        })
    return leads

def process_lead(lead):
    email = engine.hunt(lead["name"], lead["company"])
    return {
        "Name": lead["name"],
        "Email": email,
        "Company": lead["company"],
        "Role": lead["role"],
        "Intent": "HOT" if "hiring" in lead["snippet"].lower() else "COLD",
        "Status": "Verified" if email else "Not Found"
    }

def process_job(role, industry):
    leads = scrape_linkedin_leads(role, industry)
    if not leads: return []
    
    processed_leads = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        processed_leads = list(executor.map(process_lead, leads))

    # Save to Database
    if processed_leads:
        import sqlite3
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        # Ensure table exists
        c.execute('''CREATE TABLE IF NOT EXISTS leads
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      Name TEXT, Email TEXT, Company TEXT, Role TEXT, Intent TEXT, Status TEXT)''')
        
        for lead in processed_leads:
            c.execute("INSERT INTO leads (Name, Email, Company, Role, Intent, Status) VALUES (?, ?, ?, ?, ?, ?)",
                      (lead['Name'], lead['Email'], lead['Company'], lead['Role'], lead['Intent'], lead['Status']))
        conn.commit()
        conn.close()
        
    return processed_leads