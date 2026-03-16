import requests

COOKIES = [
    {"name": "c_user", "value": "1654067835", "domain": ".facebook.com", "path": "/"},
    {"name": "datr", "value": "QKZFaQHJiY2FIdRrLfIXgmeu", "domain": ".facebook.com", "path": "/"},
    {"name": "fr", "value": "1xl4w9nO44xgvB7J1.AWd-A2ID1std2WJu1EA2JMixbAWZi-r0s6EeNZCmTZLG-Uxp-18.Bpt_ua..AAA.0.0.Bpt_0E.AWfMaxGY0_k32hh4WZ_rXI_kFJo", "domain": ".facebook.com", "path": "/"},
    {"name": "sb", "value": "QKZFaUvyXOZx-HeGc3mASYmy", "domain": ".facebook.com", "path": "/"},
    {"name": "xs", "value": "20%3ACsBVpW1qsZ64cQ%3A2%3A1772710597%3A-1%3A-1%3A%3AAcyQxeZY1Mk9FduKfOM9DaUsKsDA6VzCXZj00ji8SEc", "domain": ".facebook.com", "path": "/"}
]

jar = requests.cookies.RequestsCookieJar()
for c in COOKIES:
    jar.set(c['name'], c['value'], domain=c['domain'], path=c['path'])

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
}

urls = [
    "https://mbasic.facebook.com/profile.php?id=100046769209431",
    "https://mbasic.facebook.com/profile.php?id=100064401923269"
]

for url in urls:
    print(f"--- Checking {url} ---")
    try:
        r = requests.get(url, cookies=jar, headers=headers, timeout=20)
        print(f"Status Code: {r.status_code}")
        print(f"Final URL: {r.url}")
        print(f"Content Length: {len(r.text)}")
        if "login" in r.url.lower() or "checkpoint" in r.url.lower():
            print("Blocked by Login/Checkpoint")
        elif "Log In" in r.text or "Sign Up" in r.text:
            print("Found 'Log In' or 'Sign Up' in text - likely blocked")
        else:
            print("Appears to be logged in or public page")
            print(f"Title: {r.text.split('<title>')[1].split('</title>')[0] if '<title>' in r.text else 'No Title'}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)
