import os
import time
from playwright.sync_api import sync_playwright
from feedgenerator import Rss201rev2Feed
from datetime import datetime
import json

# --- CONFIGURATION ---
PAGES = [
    {"id": "100046769209431", "name": "Mr Bro"},
    {"id": "100064401923269", "name": "PUBG MOBILE"}
]

# Provided Facebook Cookies
COOKIES = [
    {"name": "c_user", "value": "1654067835", "domain": ".facebook.com", "path": "/"},
    {"name": "datr", "value": "QKZFaQHJiY2FIdRrLfIXgmeu", "domain": ".facebook.com", "path": "/"},
    {"name": "fr", "value": "1xl4w9nO44xgvB7J1.AWd-A2ID1std2WJu1EA2JMixbAWZi-r0s6EeNZCmTZLG-Uxp-18.Bpt_ua..AAA.0.0.Bpt_0E.AWfMaxGY0_k32hh4WZ_rXI_kFJo", "domain": ".facebook.com", "path": "/"},
    {"name": "sb", "value": "QKZFaUvyXOZx-HeGc3mASYmy", "domain": ".facebook.com", "path": "/"},
    {"name": "xs", "value": "20%3ACsBVpW1qsZ64cQ%3A2%3A1772710597%3A-1%3A-1%3A%3AAcyQxeZY1Mk9FduKfOM9DaUsKsDA6VzCXZj00ji8SEc", "domain": ".facebook.com", "path": "/"}
]

def scrape_fb():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
        )
        
        # Add Cookies to the context
        context.add_cookies(COOKIES)
        page = context.new_page()

        for fb_page in PAGES:
            print(f"Scraping {fb_page['name']} with Cookies...")
            url = f"https://mbasic.facebook.com/profile.php?id={fb_page['id']}"
            
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Check if still logged in
                if "login" in page.url.lower() and not page.query_selector('article'):
                    print(f"Cookie might be expired for {fb_page['name']}")

                feed = Rss201rev2Feed(
                    title=f"{fb_page['name']} Facebook Feed",
                    link=f"https://facebook.com/{fb_page['id']}",
                    description=f"Latest posts from {fb_page['name']} (Authenticated)",
                    language="en",
                )

                # Scrape posts
                posts = page.query_selector_all('div[role="article"], article, .story_body_container')
                print(f"Found {len(posts)} posts for {fb_page['name']}")

                count = 0
                for post in posts:
                    if count >= 15: break
                    try:
                        inner_text = post.inner_text()
                        lines = [l.strip() for l in inner_text.split('\n') if len(l.strip()) > 3]
                        
                        # Filter out common UI words
                        garbage = ["Like", "Comment", "Share", "Full Story", "More", "React"]
                        clean_lines = [l for l in lines if not any(g in l for g in garbage)]
                        
                        content = " ".join(clean_lines)
                        if len(content) < 10: continue

                        link_elem = post.query_selector('a[href*="story_fbid"], a[href*="fbid="], a:has-text("Full Story")')
                        post_link = f"https://facebook.com/{fb_page['id']}"
                        if link_elem:
                            raw_href = link_elem.get_attribute('href')
                            post_link = "https://m.facebook.com" + raw_href if not raw_href.startswith('http') else raw_href

                        feed.add_item(
                            title=content[:80].strip() + "...",
                            link=post_link,
                            description=content,
                            pubdate=datetime.now()
                        )
                        count += 1
                    except: continue

                if count == 0:
                    feed.add_item(title="No posts found", link=url, description="Logged in but couldn't find posts. Check layout.", pubdate=datetime.now())

                filename = f"{fb_page['name'].replace(' ', '_')}_rss.xml"
                with open(filename, "w", encoding='utf-8') as f:
                    feed.write(f, 'utf-8')
                print(f"Successfully generated {filename} with {count} items.")

            except Exception as e:
                print(f"Error: {e}")

        browser.close()

if __name__ == "__main__":
    scrape_fb()
