import sqlite3
import requests
import json
import re
import os
import time
import concurrent.futures
from email_engine import EmailEngine  # <--- IMPORT THE NEW BRAIN
from dotenv import load_dotenv # pip install python-dotenv

# --- CONFIGURATION ---
DB_NAME = "leads_database.db"
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
MAX_WORKERS = 5  # <--- SPEED: Number of simultaneous hunters

# Initialize the new Engine
engine = EmailEngine(SERPER_API_KEY)

# ---------------- DB ----------------
def init_db():
    # check_same_thread=False is required for multithreading
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY,
            name TEXT,
            role TEXT,
            company TEXT,
            url TEXT UNIQUE,
            email TEXT,
            status TEXT,
            intent_score TEXT
        )
    """)
    conn.commit()
    return conn

# ---------------- SCRAPING (YOUR PREFERRED FUNCTION) ----------------
def scrape_linkedin_leads(role, industry, limit=10):
    print(f"[*] Scraping LinkedIn for {role} in {industry}...")

    url = "https://google.serper.dev/search"
    query = f'site:linkedin.com/in "{role}" "{industry}"'
    
    payload = {"q": query, "num": limit}
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        data = r.json()
    except:
        return []

    leads = []
    
    if "organic" not in data:
        return []

    for r in data["organic"]:
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        link = r.get("link", "")
        
        # --- AGGRESSIVE PARSING LOGIC ---
        name = "Unknown"
        company = "Unknown"

        # 1. Extract Name
        delimiters = [" - ", " | ", " – "]
        for d in delimiters:
            if d in title:
                name = title.split(d)[0]
                break
        
        # 2. Extract Company from Title
        clean_title = title.replace(" | LinkedIn", "").replace(" - LinkedIn", "")
        if " - " in clean_title:
            parts = clean_title.split(" - ")
            if len(parts) >= 3:
                company = parts[-1].strip()
        
        # 3. Snippet Fallback
        if company == "Unknown" or len(company) > 40 or company in [industry, role, "LinkedIn"]:
            match = re.search(r"(?:at|of)\s+([A-Z][a-zA-Z0-9&]+(?: [A-Z][a-zA-Z0-9&]+)?)", snippet)
            if match:
                candidate = match.group(1).strip()
                if candidate.lower() not in ["the", "a", "fintech", "startup", "stealth"]:
                    company = candidate

        # 4. Experience Fallback
        if company == "Unknown" and "Experience:" in snippet:
            try:
                company = snippet.split("Experience:")[1].strip().split("·")[0].strip()
            except:
                pass

        leads.append({
            "name": name,
            "role": role,
            "company": company,
            "url": link,
            "snippet": snippet
        })

    return leads

# ---------------- WORKER FUNCTION ----------------
def process_lead(lead):
    """
    This function runs inside a separate thread.
    It handles enrichment and saving for ONE person.
    """
    # Create a new connection for this thread (SQLite rule)
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cur = conn.cursor()
    
    # Check Duplicates
    cur.execute("SELECT 1 FROM leads WHERE url=?", (lead["url"],))
    if cur.fetchone():
        conn.close()
        return None

    print(f"    🚀 Hunting: {lead['name']} @ {lead['company']}")

    # 2. Enrich (USING NEW ENGINE)
    # This crawls websites/checks DNS in parallel
    email = engine.hunt(lead["name"], lead["company"])

    intent = "HOT" if "hiring" in lead["snippet"].lower() else "COLD"

    # 3. Save
    cur.execute("""
        INSERT OR IGNORE INTO leads
        (name, role, company, url, email, status, intent_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        lead["name"],
        lead["role"],
        lead["company"],
        lead["url"],
        email,
        "new",
        intent
    ))
    
    conn.commit()
    conn.close()
    
    if email:
        return f"✅ HIT: {lead['name']} -> {email}"
    else:
        return f"❌ FAILED: {lead['name']}"

# ---------------- PIPELINE ----------------
def process_job(role, industry):
    # Initialize DB (creates table if missing)
    init_db()
    
    # 1. Scrape Batch (Fast, Single Thread)
    leads = scrape_linkedin_leads(role, industry, limit=10)
    print(f"[*] Found {len(leads)} raw leads. Igniting engine with {MAX_WORKERS} threads...")

    # 2. Parallel Enrichment (Multithreaded)
    # This launches 5 workers at once to speed up crawling
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(process_lead, leads))
    
    # Print Summary
    hits = len([r for r in results if r and "✅" in r])
    print(f"\n[*] Job Finished. Enriched {hits}/{len(leads)} leads.")

if __name__ == "__main__":
    process_job("Founder", "Fintech")