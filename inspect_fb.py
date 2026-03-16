import requests
from bs4 import BeautifulSoup

COOKIES = [
    {"name": "c_user", "value": "1654067835", "domain": ".facebook.com", "path": "/"},
    {"name": "datr", "value": "Hf63aX46V3nlHOfL2S8g4FB4", "domain": ".facebook.com", "path": "/"},
    {"name": "fr", "value": "1BLuzrdZ0Kj9TUkkH.AWc1zIN2JgnXWOlq0g5UbNLPomOPt5z3wdW_CsF1b5TNBRf0UTI.BpuHHV..AAA.0.0.BpuHHV.AWeeSsN52Vo8YnKwZBDaYhlX3EI", "domain": ".facebook.com", "path": "/"},
    {"name": "sb", "value": "QKZFaUvyXOZx-HeGc3mASYmy", "domain": ".facebook.com", "path": "/"},
    {"name": "xs", "value": "14%3AxWx93uyVT86AEw%3A2%3A1773666019%3A-1%3A-1%3A%3AAcx6beOwQuF9KgQZrYRvrrXVn938kaCq6p6-Qd2atg", "domain": ".facebook.com", "path": "/"}
]

jar = requests.cookies.RequestsCookieJar()
for c in COOKIES:
    jar.set(c['name'], c['value'], domain=c['domain'], path=c['path'])

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"
}

url = "https://mbasic.facebook.com/profile.php?id=100046769209431"
r = requests.get(url, cookies=jar, headers=headers, timeout=20)
soup = BeautifulSoup(r.text, 'html.parser')

print("=== BODY TEXT ===")
print(soup.get_text())
print("=================")
