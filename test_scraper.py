from backend_core import scrape_linkedin_leads

print("--- TESTING SCRAPER ---")
data = scrape_linkedin_leads("Marketing Director", "SaaS", limit=3)

if len(data) > 0:
    print(f"✅ SUCCESS! Found {len(data)} leads:")
    for lead in data:
        print(f"   - {lead['name']} at {lead['company']}")
else:
    print("❌ FAILURE: Still 0 results.")


