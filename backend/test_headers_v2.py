
import requests

session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Referer': 'https://www.google.com/',
    'Cache-Control': 'max-age=0',
    'DNT': '1'
}

session.headers.update(headers)

print("Visiting homepage...")
try:
    # First visit homepage to get cookies
    response = session.get("https://riyasewana.com/", timeout=10)
    print(f"Homepage Status: {response.status_code}")
    
    # Then visit search page
    url = "https://riyasewana.com/search/toyota/corolla/1995-2003"
    print(f"Fetching {url}...")
    response = session.get(url, timeout=10)
    print(f"Search Status: {response.status_code}")
    
    if response.status_code == 200:
        print("Success!")
    else:
        print("Failed.")
except Exception as e:
    print(f"Error: {e}")
