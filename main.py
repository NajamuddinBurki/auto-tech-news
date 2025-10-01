import feedparser
import schedule
import time
from datetime import datetime
from threads_api.src.threads_api import ThreadsAPI  # ✅ PyPI version import

# TechCrunch RSS feed
RSS_URL = "https://techcrunch.com/feed/"

USERNAME = "thenajamburki"
PASSWORD = "Jeju12345@"

api = ThreadsAPI()  
api.login(USERNAME, PASSWORD)

def fetch_news():
    """Fetch top 5 latest TechCrunch headlines"""
    feed = feedparser.parse(RSS_URL)
    return [entry.title for entry in feed.entries[:5]]

def create_posts_from_news():
    """Format posts for Threads"""
    headlines = fetch_news()
    return [f"📰 Tech Update: {hl}\n\n#TechNews #Innovation" for hl in headlines]

def post_to_threads(post_text):
    """Post content to Threads"""
    try:
        api.create_post(text=post_text)  # ✅ method name for PyPI
        print(f"[{datetime.now()}] ✅ Posted: {post_text[:50]}...")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error posting: {e}")

def job():
    posts = create_posts_from_news()
    if posts:
        post_to_threads(posts[0])

# Since GitHub Actions runs multiple times per day (via cron),
# we only need ONE post per run (no while loop needed).
job()
