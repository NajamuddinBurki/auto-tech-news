import feedparser
from threads_api import ThreadsAPI
import schedule
import time
from datetime import datetime

# TechCrunch RSS feed
RSS_URL = "https://techcrunch.com/feed/"

# Threads login (⚠️ keep private: use GitHub Secrets!)
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

# Schedule 5 posts a day
schedule.every().day.at("09:00").do(job)
schedule.every().day.at("13:00").do(job)
schedule.every().day.at("17:00").do(job)
schedule.every().day.at("21:00").do(job)
schedule.every().day.at("23:00").do(job)

print("✅ Scheduler started. Waiting for times...")

while True:
    schedule.run_pending()
    time.sleep(30)
