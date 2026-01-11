import requests

# ⚠️ PASTE YOUR KEYS HERE AGAIN TO BE SURE
TOMBA_KEY = "ta_8i1klu4lhglpwgxla0rkjfsekrmcretz1gs6k"
TOMBA_SECRET = "ts_b0cdbe4e-d88a-44e0-939f-8a2dc6733706"


def test_connection():
    print("--- 1. Testing Connection with a Known Hit ---")
    # We use a known person (Satya Nadella at Microsoft) to prove keys work
    url = "https://api.tomba.io/v1/email-finder"
    
    headers = {
        "content-type": "application/json",
        "X-Tomba-Key": TOMBA_KEY,
        "X-Tomba-Secret": TOMBA_SECRET
    }
    
    params = {
        "domain": "microsoft.com",
        "first_name": "Satya",
        "last_name": "Nadella"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Keys are working.")
            print(f"   Email found: {data['data']['email']}")
        elif response.status_code == 401:
            print("❌ ERROR: Unauthorized. Your API Key or Secret is wrong.")
        elif response.status_code == 429:
            print("❌ ERROR: Rate Limit. You ran out of free searches.")
        else:
            print(f"❌ ERROR: {data}")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_connection()