from playwright.sync_api import sync_playwright
import feedparser
import random
from datetime import datetime

RSS_URL = "https://techcrunch.com/feed/"

USERNAME = "your_threads_username"
PASSWORD = "your_threads_password"

def fetch_news():
    feed = feedparser.parse(RSS_URL)
    return [entry.title for entry in feed.entries[:10]]

def create_post(headline):
    return f"📰 Tech Update: {headline}\n\n#TechNews #Innovation #TechCrunch"

def post_to_threads(post_text):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.threads.net/login")
        page.fill('input[name="username"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_timeout(5000)
        page.click("text=New Thread")
        page.fill("textarea", post_text)
        page.click("text=Post")
        page.wait_for_timeout(5000)
        browser.close()
        print(f"[{datetime.now()}] Posted: {post_text[:50]}")

def job():
    headlines = fetch_news()
    if not headlines:
        print("⚠️ No headlines fetched")
        return
    headline = random.choice(headlines)
    post_text = create_post(headline)
    print(f"Posting: {post_text[:50]}")
    post_to_threads(post_text)

if __name__ == "__main__":
    job()
