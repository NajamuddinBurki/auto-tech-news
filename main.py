import feedparser
from threads_api import ThreadsAPI
from datetime import datetime

# TechCrunch RSS feed
RSS_URL = "https://techcrunch.com/feed/"

# Threads login (⚠️ put in GitHub Secrets if repo is public)
USERNAME = "thenajamburki"
PASSWORD = "Jeju12345@"

api = ThreadsAPI(username=USERNAME, password=PASSWORD)

def fetch_news():
    feed = feedparser.parse(RSS_URL)
    headlines = [entry.title for entry in feed.entries[:5]]
    return headlines

def create_posts_from_news():
    headlines = fetch_news()
    return [f"📰 Tech Update: {hl}\n\n#TechNews #Innovation" for hl in headlines]

def post_to_threads(post_text):
    try:
        api.post(text=post_text)
        print(f"[{datetime.now()}] ✅ Posted: {post_text[:50]}...")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error posting: {e}")

def job():
    posts = create_posts_from_news()
    if posts:
        post_to_threads(posts[0])

if __name__ == "__main__":
    job()
