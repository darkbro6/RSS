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

def scrape_fb():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a more realistic user agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
        )
        page = context.new_page()

        for fb_page in PAGES:
            print(f"Scraping {fb_page['name']}...")
            # Using m.facebook.com instead of mbasic as a fallback test
            url = f"https://mbasic.facebook.com/profile.php?id={fb_page['id']}"
            
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Debug: Check if we are blocked
                if "login" in page.url.lower() or page.query_selector('input[name="email"]'):
                    print(f"Blocked by login wall for {fb_page['name']}")
                
                feed = Rss201rev2Feed(
                    title=f"{fb_page['name']} Facebook Feed",
                    link=f"https://facebook.com/{fb_page['id']}",
                    description=f"Latest posts from {fb_page['name']}",
                    language="en",
                )

                # More aggressive searching for posts
                # mbasic posts are usually inside divs with specific data-ft attributes or just articles
                posts = page.query_selector_all('div[role="article"], article, .story_body_container')
                
                print(f"Found {len(posts)} potential post elements for {fb_page['name']}")

                count = 0
                for post in posts:
                    if count >= 15: break
                    
                    try:
                        # Find all text inside the post container
                        text_parts = post.inner_text().split('\n')
                        # Filter out very short strings like "Like", "Comment", etc.
                        content = " ".join([p for p in text_parts if len(p) > 20])
                        
                        if not content or len(content) < 10:
                            # Try to find specific span/p if generic fail
                            elem = post.query_selector('p, span')
                            content = elem.inner_text() if elem else "Facebook Update (Image/Link only)"

                        # Find any link in the post footer/header
                        link_elem = post.query_selector('a[href*="story_fbid"], a[href*="fbid="], a:has-text("Full Story")')
                        post_link = f"https://facebook.com/{fb_page['id']}"
                        if link_elem:
                            raw_href = link_elem.get_attribute('href')
                            if "facebook.com" in raw_href:
                                post_link = raw_href
                            else:
                                post_link = "https://m.facebook.com" + raw_href

                        feed.add_item(
                            title=content[:80].strip() + "...",
                            link=post_link,
                            description=content,
                            pubdate=datetime.now()
                        )
                        count += 1
                    except Exception as e:
                        continue

                # If still empty, add a dummy item to show it's working but empty
                if count == 0:
                    feed.add_item(
                        title="Feed is currently empty",
                        link=url,
                        description="Could not find any posts. This might be due to Facebook's login wall or layout change.",
                        pubdate=datetime.now()
                    )

                filename = f"{fb_page['name'].replace(' ', '_')}_rss.xml"
                with open(filename, "w", encoding='utf-8') as f:
                    feed.write(f, 'utf-8')
                print(f"Generated {filename} with {count} items.")

            except Exception as e:
                print(f"Error scraping {fb_page['name']}: {e}")

        browser.close()

if __name__ == "__main__":
    scrape_fb()
