import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Try standard mobile site or mbasic
url = "https://m.facebook.com/PUBGMOBILE/posts/"
print(f"Checking {url}...")
try:
    r = requests.get(url, headers=headers, timeout=20)
    print(f"Status Code: {r.status_code}")
    print(f"Final URL: {r.url}")
    print(f"Content Length: {len(r.text)}")
    if "login" in r.url.lower():
        print("Redirected to login")
    else:
        print(f"Title: {r.text.split('<title>')[1].split('</title>')[0] if '<title>' in r.text else 'No Title'}")
        if "PUBG MOBILE" in r.text:
            print("Found 'PUBG MOBILE' in text")
except Exception as e:
    print(f"Error: {e}")
