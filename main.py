import feedparser
from threads_api import ThreadsAPI
from datetime import datetime
import random

# TechCrunch RSS feed
RSS_URL = "https://techcrunch.com/feed/"

# Threads login (⚠️ best to use GitHub Secrets in production!)
USERNAME = "thenajamburki"
PASSWORD = "Jeju12345@"

api = ThreadsAPI(username=USERNAME, password=PASSWORD)

def fetch_news():
    """Fetch the latest headlines from TechCrunch RSS"""
    feed = feedparser.parse(RSS_URL)
    headlines = [entry.title for entry in feed.entries[:10]]  # get top 10
    return headlines

def create_post_from_headline(headline):
    """Format the post text"""
    return f"📰 Tech Update: {headline}\n\n#TechNews #Innovation #TechCrunch"

def post_to_threads(post_text):
    """Send post to Threads"""
    try:
        api.post(text=post_text)
        print(f"[{datetime.now()}] ✅ Posted: {post_text[:50]}...")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error posting: {e}")

def job():
    """Main job that picks a random headline and posts"""
    headlines = fetch_news()
    if not headlines:
        print("⚠️ No headlines fetched.")
        return
    
    # pick a random headline each time
    headline = random.choice(headlines)
    post_text = create_post_from_headline(headline)
    post_to_threads(post_text)

if __name__ == "__main__":
    job()  # runs once (GitHub Actions handles timing)
