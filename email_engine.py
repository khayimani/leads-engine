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

# --- CONFIGURATION ---
TIMEOUT = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# --- REGEX ---
# Catches: name@domain.com, name[at]domain.com, name(at)domain.com
EMAIL_REGEX = re.compile(r'([a-zA-Z0-9._%+-]+(?:\s*[@\[\(]\s*at\s*[\)\]]\s*|\s*@\s*)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', re.IGNORECASE)

class EmailEngine:
    def __init__(self, serper_key):
        self.serper_key = serper_key

    def _clean_email(self, raw_email):
        """Fixes obfuscated emails like 'john [at] stripe.com'"""
        email = raw_email.lower()
        email = re.sub(r'\s*[@\[\(]\s*at\s*[\)\]]\s*', '@', email)
        return email.strip()

    def get_canonical_domain(self, company_name):
        """LAYER 1: DOMAIN RESOLUTION"""
        print(f"    🌍 Resolving domain for: {company_name}...")
        url = "https://google.serper.dev/search"
        payload = {"q": f"{company_name} official site", "num": 1}
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
            data = r.json()
            if "organic" in data and len(data["organic"]) > 0:
                link = data["organic"][0]["link"]
                domain = urlparse(link).netloc.replace("www.", "")
                return domain
        except:
            pass
        return None

    def verify_mx(self, domain):
        """LAYER 4: MX RECORD CHECK (Pass/Fail)"""
        try:
            records = dns.resolver.resolve(domain, 'MX')
            return True if records else False
        except:
            return False

    def crawl_site(self, domain, target_name):
        """LAYER 2: PAGE-LEVEL EXTRACTION"""
        print(f"    🕷️ Crawling {domain} for contact info...")
        
        # Priority Pages
        paths = ["", "/contact", "/about", "/team", "/people", "/leadership"]
        found_emails = set()
        
        base_url = f"https://{domain}"
        
        for path in paths:
            target_url = urljoin(base_url, path)
            try:
                r = requests.get(target_url, headers=HEADERS, timeout=5)
                if r.status_code != 200: continue
                
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text(" ", strip=True) # Get text only
                
                # Extract
                matches = EMAIL_REGEX.findall(text)
                for m in matches:
                    clean = self._clean_email(m)
                    if domain in clean: # Only keep company emails
                        found_emails.add(clean)
                        
            except:
                continue
                
        # Filter: If we found emails, try to match the Target Name
        if not found_emails:
            return None
            
        print(f"    -> Found {len(found_emails)} raw emails on site.")
        
        # Split target name: "Steve McLaughlin" -> "steve", "mclaughlin"
        parts = target_name.lower().split()
        if not parts: return list(found_emails)[0] # Return random valid one if name breaks
        
        first = parts[0]
        last = parts[-1] if len(parts) > 1 else ""

        # Score the emails
        best_email = None
        highest_score = 0
        
        for email in found_emails:
            score = 0
            if first in email: score += 50
            if last and last in email: score += 50
            if "info" in email or "contact" in email: score -= 10 # Penalize generics
            
            if score > highest_score:
                highest_score = score
                best_email = email
                
        # If no personal match, return generic (Layer 5)
        if highest_score < 50:
            generics = [e for e in found_emails if "info" in e or "contact" in e or "hello" in e]
            if generics: return generics[0]
            
        return best_email

    def heuristic_guess(self, name, domain):
        """LAYER 3: PERMUTATION GUESSING"""
        parts = name.lower().split()
        if len(parts) < 2: return None
        
        f = parts[0]
        l = parts[-1]
        
        # Most common B2B patterns
        guesses = [
            f"{f}@{domain}",       # steve@ftpartners.com
            f"{f}.{l}@{domain}",   # steve.mclaughlin@ftpartners.com
            f"{f[0]}{l}@{domain}", # smclaughlin@ftpartners.com
        ]
        
        # In a real SaaS, you would ping an SMTP validator here.
        # For now, we return the most likely (First.Last is standard for 80% of corps)
        return guesses[1] 

    def hunt(self, name, company):
        # 1. Get Domain
        domain = self.get_canonical_domain(company)
        if not domain: return None
        
        # 2. Verify Domain exists (MX Check)
        if not self.verify_mx(domain):
            print(f"    ⚠️ Domain {domain} has no mail servers.")
            return None
            
        # 3. Crawl Site (High Confidence)
        email = self.crawl_site(domain, name)
        if email: 
            return email
            
        # 4. Fallback to Heuristic (Low Confidence but better than nothing)
        print(f"    🎲 Crawl failed. Guessing format...")
        return self.heuristic_guess(name, domain)