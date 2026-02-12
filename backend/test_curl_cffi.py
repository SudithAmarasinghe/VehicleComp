
from curl_cffi import requests

url = "https://riyasewana.com/search/toyota/corolla/1995-2003"
print(f"Fetching {url} with curl_cffi...")

try:
    response = requests.get(
        url,
        impersonate="chrome110",
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Page content length:", len(response.content))
    else:
        print("Failed.")
except Exception as e:
    print(f"Error: {e}")
