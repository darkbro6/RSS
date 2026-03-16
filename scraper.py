import os
import time
from playwright.sync_api import sync_playwright
from feedgenerator import Rss201rev2Feed
from datetime import datetime
import re

# --- CONFIGURATION ---
PAGES = [
    {"id": "100046769209431", "name": "Mr Bro"},
    {"id": "100064401923269", "name": "PUBG MOBILE"}
]

def scrape_fb():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for fb_page in PAGES:
            print(f"Scraping {fb_page['name']}...")
            # We use mbasic for easier scraping without heavy JS
            url = f"https://mbasic.facebook.com/profile.php?id={fb_page['id']}"
            
            try:
                page.goto(url, wait_until="networkidle")
                
                feed = Rss201rev2Feed(
                    title=f"{fb_page['name']} Facebook Feed",
                    link=f"https://facebook.com/{fb_page['id']}",
                    description=f"Latest posts from {fb_page['name']} (Generated via GitHub Actions)",
                    language="en",
                )

                # Find post articles
                # mbasic uses 'article' or specific divs for posts
                posts = page.query_selector_all('article, .story_body_container')
                
                if not posts:
                    print(f"No posts found for {fb_page['name']}. Might be blocked or layout changed.")
                    # Fallback to a simpler check
                    if "Login" in page.title():
                        print("Hit Login Wall. Consider adding cookies.")

                count = 0
                for post in posts:
                    if count >= 10: break # Limit to 10 latest posts
                    
                    try:
                        # Extract Content
                        # In mbasic, text is often in a div with some specific styling or just a div inside the article
                        content_element = post.query_selector('div > span, p')
                        content = content_element.inner_text() if content_element else "No text content"
                        
                        # Extract Link
                        # Look for "Full Story" or "More" link
                        link_element = post.query_selector('footer a[href*="story_fbid"], a:has-text("Full Story")')
                        if not link_element:
                           link_element = post.query_selector('a[href*="/story.php"]')
                           
                        post_link = url
                        if link_element:
                            href = link_element.get_attribute('href')
                            if href.startswith('/'):
                                post_link = "https://m.facebook.com" + href
                            else:
                                post_link = href

                        # Add to RSS feed
                        feed.add_item(
                            title=content[:70] + ("..." if len(content) > 70 else ""),
                            link=post_link,
                            description=content,
                            pubdate=datetime.now() # mbasic doesn't always show precise timestamps easily
                        )
                        count += 1
                    except Exception as e:
                        print(f"Error parsing post for {fb_page['name']}: {e}")

                # Save as XML file
                filename = f"{fb_page['name'].replace(' ', '_')}_rss.xml"
                with open(filename, "w", encoding='utf-8') as f:
                    feed.write(f, 'utf-8')
                print(f"Successfully generated {filename}")

            except Exception as e:
                print(f"Failed to scrape {fb_page['name']}: {e}")

        browser.close()

if __name__ == "__main__":
    scrape_fb()
