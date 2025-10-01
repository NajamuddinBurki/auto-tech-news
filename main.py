import feedparser
from threads_api.src.threads_api import ThreadsAPI
from datetime import datetime
import random

# TechCrunch RSS feed
RSS_URL = "https://techcrunch.com/feed/"

# ⚠️ For production, move these into GitHub Secrets!
USERNAME = "thenajamburki"
PASSWORD = "Jeju12345@"

print("🚀 Starting auto-poster script...")

# Step 1: Try login
try:
    print("🔑 Logging into Threads...")
    api = ThreadsAPI(username=USERNAME, password=PASSWORD)
    print("✅ Login successful!")
except Exception as e:
    print(f"❌ Login failed: {e}")
    exit(1)

def fetch_news():
    """Fetch latest headlines from TechCrunch"""
    print("🌐 Fetching TechCrunch headlines...")
    feed = feedparser.parse(RSS_URL)
    headlines = [entry.title for entry in feed.entries[:10]]
    if headlines:
        print(f"✅ Retrieved {len(headlines)} headlines")
    else:
        print("⚠️ No headlines found in feed!")
    return headlines

def create_post(headline):
    """Format the post text"""
    return f"📰 Tech Update: {headline}\n\n#TechNews #Innovation #TechCrunch"

def post_to_threads(post_text):
    """Send post to Threads"""
    try:
        print("📤 Attempting to post to Threads...")
        api.post(text=post_text)
        print(f"[{datetime.now()}] ✅ Posted successfully: {post_text[:50]}...")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error posting: {e}")

def job():
    """Pick one random headline and post it"""
    headlines = fetch_news()
    if headlines:
        headline = random.choice(headlines)
        print(f"✏️ Preparing post: {headline[:50]}...")
        post_text = create_post(headline)
        post_to_threads(post_text)
    else:
        print("⚠️ Skipping post (no headlines).")

if __name__ == "__main__":
    job()
