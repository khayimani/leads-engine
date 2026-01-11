import requests
import json
import re
import concurrent.futures
import random
from email_engine import EmailEngine

# --- CONFIGURATION ---
SERPER_API_KEY = "e3b6016ca8de93b72ee9d85593448539c84160f8"
MAX_WORKERS = 5

engine = EmailEngine(SERPER_API_KEY)

# ---------------- SCRAPER ----------------
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
    if "organic" not in data: return []

    for r in data["organic"]:
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        link = r.get("link", "")
        
        # --- PARSING ---
        clean_title = title.replace(" | LinkedIn", "").replace(" - LinkedIn", "")
        parts = clean_title.split(" - ")
        name = parts[0]
        
        company = "Unknown"
        if len(parts) >= 3:
            company = parts[-1].strip()
        
        # Fallback to snippet if company is missing
        if company == "Unknown":
            match = re.search(r"(?:at|of)\s+([A-Z][a-zA-Z0-9&]+(?: [A-Z][a-zA-Z0-9&]+)?)", snippet)
            if match:
                candidate = match.group(1).strip()
                if candidate.lower() not in ["the", "a", "fintech", "startup"]:
                    company = candidate

        leads.append({
            "name": name,
            "role": role,
            "company": company,
            "url": link,
            "snippet": snippet
        })
    return leads

# ---------------- WORKER ----------------
def process_lead(lead):
    """Enriches a single lead in memory."""
    # Run the engine
    email = engine.hunt(lead["name"], lead["company"])
    intent = "HOT" if "hiring" in lead["snippet"].lower() else "COLD"
    
    # Return a dictionary (Row of data)
    return {
        "Name": lead["name"],
        "Role": lead["role"],
        "Company": lead["company"],
        "Email": email,
        "Status": "Verified" if email else "Not Found",
        "Intent": intent,
        "URL": lead["url"]
    }

# ---------------- PIPELINE ----------------
def process_job(role, industry):
    """
    Runs the full job and RETURNS a list of dictionaries.
    CRITICAL: This must return a list, NOT save to DB.
    """
    # 1. Scrape
    leads = scrape_linkedin_leads(role, industry, limit=10)
    
    if not leads:
        return [] # Return empty list if no leads found

    # 2. Enrich (Parallel)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # map returns results in the same order as inputs
        processed = list(executor.map(process_lead, leads))
        results.extend(processed)
        
    return results  # <--- THIS IS THE FIX. The old code didn't have this.