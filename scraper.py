import os
import time
from playwright.sync_api import sync_playwright
from feedgenerator import Rss201rev2Feed
from datetime import datetime

# --- CONFIGURATION ---
PAGES = [
    {"id": "100046769209431", "name": "Mr Bro"},
    {"id": "100064401923269", "name": "PUBG MOBILE"}
]

# Provided Facebook Cookies
COOKIES = [
    {"name": "c_user", "value": "1654067835", "domain": ".facebook.com", "path": "/"},
    {"name": "datr", "value": "Hf63aX46V3nlHOfL2S8g4FB4", "domain": ".facebook.com", "path": "/"},
    {"name": "fr", "value": "1BLuzrdZ0Kj9TUkkH.AWc1zIN2JgnXWOlq0g5UbNLPomOPt5z3wdW_CsF1b5TNBRf0UTI.BpuHHV..AAA.0.0.BpuHHV.AWeeSsN52Vo8YnKwZBDaYhlX3EI", "domain": ".facebook.com", "path": "/"},
    {"name": "sb", "value": "QKZFaUvyXOZx-HeGc3mASYmy", "domain": ".facebook.com", "path": "/"},
    {"name": "xs", "value": "14%3AxWx93uyVT86AEw%3A2%3A1773666019%3A-1%3A-1%3A%3AAcx6beOwQuF9KgQZrYRvrrXVn938kaCq6p6-Qd2atg", "domain": ".facebook.com", "path": "/"}
]

def scrape_fb():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a more modern and common mobile user agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            viewport={'width': 414, 'height': 896}
        )
        context.add_cookies(COOKIES)
        page = context.new_page()

        for fb_page in PAGES:
            print(f"--- Scraping {fb_page['name']} ---")
            # Try direct ID URL which is often more reliable on mbasic
            url = f"https://mbasic.facebook.com/{fb_page['id']}"
            
            try:
                print(f"Loading {url}...")
                page.goto(url, wait_until="networkidle", timeout=60000)
                time.sleep(3) # Initial wait
                
                # Scroll down a bit to trigger any lazy loading (less common in mbasic but good for m.)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                time.sleep(2)

                print(f"Page Title: {page.title()}")
                print(f"Current URL: {page.url}")

                is_blocked = "login" in page.url.lower() or "checkpoint" in page.url.lower()
                if is_blocked:
                    print("!!! ALERT: Blocked by Login/Checkpoint Wall. Cookies might be expired. !!!")
                
                feed = Rss201rev2Feed(
                    title=f"{fb_page['name']} Facebook Feed",
                    link=f"https://facebook.com/{fb_page['id']}",
                    description=f"Latest posts from {fb_page['name']} (Authenticated: {not is_blocked})",
                    language="en",
                )

                # Expanded selectors for different Facebook mobile layouts
                selectors = [
                    'article', 
                    'div[role="article"]', 
                    '.story_body_container', 
                    'div[data-ft]', 
                    'div.msg',
                    'section > div > div > div', # common nested structure
                    '#m_group_stories_container > div'
                ]
                
                potential_posts = []
                for sel in selectors:
                    found = page.query_selector_all(sel)
                    if found:
                        print(f"  Found {len(found)} candidates with selector: {sel}")
                        potential_posts.extend(found)
                        if len(potential_posts) > 10: break
                
                # Deduplicate based on text content to avoid overlapping selectors
                seen_texts = set()
                unique_posts = []
                for p_node in potential_posts:
                    try:
                        txt = p_node.inner_text().strip()
                        if len(txt) > 20 and txt not in seen_texts:
                            seen_texts.add(txt)
                            unique_posts.append(p_node)
                    except: continue

                print(f"Total unique potential items: {len(unique_posts)}")

                count = 0
                for post in unique_posts:
                    if count >= 15: break
                    try:
                        full_text = post.inner_text().strip()
                        
                        # Clean UI text and noise
                        lines = [l.strip() for l in full_text.split('\n') if len(l.strip()) > 2]
                        forbidden = [
                            "Like", "Comment", "Share", "Full Story", "More", 
                            "React", "View", "replies", "Send", "Message",
                            "Join", "Follow", "Sign Up", "Log In"
                        ]
                        content_lines = [l for l in lines if not any(f.lower() in l.lower() for f in forbidden)]
                        content = " ".join(content_lines)
                        
                        if len(content) < 10: continue

                        # Link extraction - try to find the timestamp or "Full Story" link
                        link_elem = post.query_selector('a[href*="story_fbid"], a[href*="fbid="], a:has-text("Full Story"), a:has-text("More"), a:has-text("...")')
                        post_link = f"https://facebook.com/{fb_page['id']}"
                        if link_elem:
                            href = link_elem.get_attribute('href')
                            if href:
                                if href.startswith('/'):
                                    post_link = "https://m.facebook.com" + href
                                else:
                                    post_link = href

                        feed.add_item(
                            title=(content[:75] + '...') if len(content) > 75 else content,
                            link=post_link,
                            description=content,
                            pubdate=datetime.now()
                        )
                        count += 1
                        print(f"    [+] Added post {count}: {content[:40]}...")
                    except Exception as e: 
                        continue

                if count == 0:
                    status_msg = "Blocked" if is_blocked else "Logged in but no posts found"
                    print(f"!!! No posts found for {fb_page['name']} ({status_msg})")
                    feed.add_item(
                        title=f"Status: {status_msg}",
                        link=page.url,
                        description=f"Title: {page.title()} | URL: {page.url} | Content Length: {len(page.content())}. Check if cookies are expired or if the page layout changed.",
                        pubdate=datetime.now()
                    )

                filename = f"{fb_page['name'].replace(' ', '_')}_rss.xml"
                with open(filename, "w", encoding='utf-8') as f:
                    feed.write(f, 'utf-8')
                print(f"Generated {filename}")

            except Exception as e:
                print(f"Error for {fb_page['name']}: {e}")

        browser.close()

if __name__ == "__main__":
    scrape_fb()
