import feedparser
import schedule
import time

# ✅ Flexible import for ThreadsAPI
try:
    from threads_api import ThreadsAPI  # some builds expose it here
except ImportError:
    from threads_api.src.threads_api import ThreadsAPI  # fallback for PyPI/src layout

# Load credentials from environment variables
import os
USERNAME = os.getenv("THREADS_USERNAME")
PASSWORD = os.getenv("THREADS_PASSWORD")

# Initialize API (no username/password args, login is separate)
api = ThreadsAPI()
api.login(USERNAME, PASSWORD)  # ✅ login call

# Example: Fetch TechCrunch feed
RSS_FEED = "https://techcrunch.com/feed/"

def post_latest_news():
    feed = feedparser.parse(RSS_FEED)
    if not feed.entries:
        print("[WARN] No entries found in RSS feed")
        return

    latest = feed.entries[0]
    title = latest.title
    link = latest.link
    content = f"{title}\n\nRead more: {link}"

    try:
        api.post(content)  # ✅ correct method (not create_post)
        print(f"[INFO] Posted: {title}")
    except Exception as e:
        print(f"[ERROR] Failed to post: {e}")

# Schedule job every hour
schedule.every(1).hours.do(post_latest_news)

print("[INFO] Auto Tech News Poster started...")

while True:
    schedule.run_pending()
    time.sleep(30)
