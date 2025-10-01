import feedparser
from threads_api.src.threads_api import ThreadsAPI
from datetime import datetime
import random

RSS_URL = "https://techcrunch.com/feed/"

USERNAME = "thenajamburki"
PASSWORD = "Jeju12345@"

api = ThreadsAPI(username=USERNAME, password=PASSWORD)

def fetch_news():
    feed = feedparser.parse(RSS_URL)
    return [entry.title for entry in feed.entries[:10]]

def create_post(headline):
    return f"📰 Tech Update: {headline}\n\n#TechNews #Innovation #TechCrunch"

def post_to_threads(post_text):
    try:
        api.post(text=post_text)
        print(f"[{datetime.now()}] ✅ Posted: {post_text[:50]}...")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error: {e}")

def job():
    headlines = fetch_news()
    if headlines:
        headline = random.choice(headlines)
        post_to_threads(create_post(headline))
    else:
        print("⚠️ No headlines fetched.")

if __name__ == "__main__":
    job()
