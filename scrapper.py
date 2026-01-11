from duckduckgo_search import DDGS
import pandas as pd
import time

# --- CONFIGURATION ---
TARGET_ROLE = "Marketing Director"
TARGET_INDUSTRY = "E-commerce"
TARGET_PLATFORM = "site:linkedin.com/in"  # Change to site:twitter.com for X
MAX_RESULTS = 20

# Categorization Logic: Keywords that signal buying intent or growth
INTENT_SIGNALS = {
    'HIGH': ['hiring', 'growing', 'scaling', 'looking for', 'we need'],
    'MEDIUM': ['building', 'founder', 'head of', 'launching'],
    'LOW': ['enthusiast', 'student', 'intern', 'seeking opportunities']
}

def get_leads(role, industry, limit=10):
    query = f'{TARGET_PLATFORM} "{role}" "{industry}"'
    print(f"[*] Searching: {query}...")
    
    results = []
    # Use DDGS context manager to perform search
    with DDGS() as ddgs:
        # scraping the search results
        search_gen = ddgs.text(query, max_results=limit)
        for r in search_gen:
            results.append({
                'title': r['title'],
                'link': r['href'],
                'snippet': r['body']
            })
    return results

def categorize_lead(text):
    text = text.lower()
    
    # Check High Intent
    for keyword in INTENT_SIGNALS['HIGH']:
        if keyword in text:
            return "HOT (Active Intent)"
            
    # Check Medium Intent
    for keyword in INTENT_SIGNALS['MEDIUM']:
        if keyword in text:
            return "WARM (Decision Maker)"
            
    # Check Low Intent
    for keyword in INTENT_SIGNALS['LOW']:
        if keyword in text:
            return "COLD (Irrelevant)"
            
    return "UNCATEGORIZED"

def main():
    # 1. Scrape
    raw_leads = get_leads(TARGET_ROLE, TARGET_INDUSTRY, MAX_RESULTS)
    
    processed_data = []
    
    # 2. Process & Categorize
    for lead in raw_leads:
        category = categorize_lead(lead['snippet'] + lead['title'])
        processed_data.append({
            'Name/Title': lead['title'],
            'Category': category,
            'Snippet': lead['snippet'],
            'URL': lead['link']
        })
        
    # 3. Output
    df = pd.DataFrame(processed_data)
    
    # Display simplified view
    print("\n--- GENERATED LEADS ---")
    print(df[['Name/Title', 'Category']].to_string(index=False))
    
    # Save to CSV for manual outreach
    df.to_csv("classified_leads.csv", index=False)
    print("\n[*] Data saved to classified_leads.csv")

if __name__ == "__main__":
    main()