import requests
import re
import dns.resolver
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
]

TIMEOUT = 10
EMAIL_REGEX = re.compile(r'([a-zA-Z0-9._%+-]+(?:\s*[@\[\(]\s*at\s*[\)\]]\s*|\s*@\s*)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', re.IGNORECASE)

class EmailEngine:
    def __init__(self, serper_key):
        self.serper_key = serper_key

    def _clean_email(self, raw_email):
        email = raw_email.lower()
        email = re.sub(r'\s*[@\[\(]\s*at\s*[\)\]]\s*', '@', email)
        return email.strip()

    def get_canonical_domain(self, company_name):
        print(f"    🌍 Resolving domain for: {company_name}...")
        url = "https://google.serper.dev/search"
        payload = {"q": f"{company_name} official site", "num": 1}
        # FIXED: Added X-API-KEY header
        headers = {"X-API-KEY": self.serper_key, "Content-Type": "application/json", "User-Agent": random.choice(USER_AGENTS)}
        
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()
            if "organic" in data and len(data["organic"]) > 0:
                link = data["organic"][0]["link"]
                domain = urlparse(link).netloc.replace("www.", "")
                return domain
        except Exception as e:
            print(f"    ❌ Domain Resolution Error: {e}")
        return None

    def verify_mx(self, domain):
        try:
            records = dns.resolver.resolve(domain, 'MX')
            return True if records else False
        except Exception:
            return False

    def crawl_site(self, domain, target_name):
        print(f"    🕷️ Crawling {domain}...")
        paths = ["", "/contact", "/about", "/team", "/people"]
        found_emails = set()
        
        for path in paths:
            try:
                r = requests.get(urljoin(f"https://{domain}", path), headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=5)
                if r.status_code != 200: continue
                soup = BeautifulSoup(r.text, 'html.parser')
                matches = EMAIL_REGEX.findall(soup.get_text(" "))
                for m in matches:
                    clean = self._clean_email(m)
                    # FIXED: Changed 'domain in clean' to 'endswith' to catch subdomains
                    if clean.endswith(domain):
                        found_emails.add(clean)
            except Exception:
                continue
                
        if not found_emails: return None
        
        parts = target_name.lower().split()
        first = parts[0] if parts else ""
        last = parts[-1] if len(parts) > 1 else ""

        best_email, highest_score = None, 0
        for email in found_emails:
            score = 0
            if first and first in email: score += 50
            if last and last in email: score += 50
            if any(x in email for x in ["info", "contact", "hello"]): score -= 10
            if score > highest_score:
                highest_score, best_email = score, email
                
        return best_email if highest_score > 0 else list(found_emails)[0]

    def heuristic_guess(self, name, domain):
        parts = name.lower().split()
        if len(parts) < 2: return None
        f, l = parts[0], parts[-1]
        # Common pattern: first.last@domain
        return f"{f}.{l}@{domain}"

    def hunt(self, name, company):
        if not company or company == "Unknown": return None
        domain = self.get_canonical_domain(company)
        if not domain or not self.verify_mx(domain): return None
        
        email = self.crawl_site(domain, name)
        if email: return email
        
        print(f"    🎲 Crawl failed. Guessing...")
        return self.heuristic_guess(name, domain)