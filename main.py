import asyncio
import feedparser
import schedule
import time
import os

# ✅ Patch: Ensure event loop exists
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Flexible import for ThreadsAPI
try:
    from threads_api import ThreadsAPI
except ImportError:
    from threads_api.src.threads_api import ThreadsAPI

USERNAME = os.getenv("THREADS_USERNAME")
PASSWORD = os.getenv("THREADS_PASSWORD")

api = ThreadsAPI()

# Wrap login into asyncio loop
async def login():
    await api.login(USERNAME, PASSWORD)

asyncio.get_event_loop().run_until_complete(login())

# RSS feed
RSS_FEED = "https://techcrunch.com/feed/"

async def post_latest_news():
    feed = feedparser.parse(RSS_FEED)
    if not feed.entries:
        print("[WARN] No entries found in RSS feed")
        return

    latest = feed.entries[0]
    title = latest.title
    link = latest.link
    content = f"{title}\n\nRead more: {link}"

    try:
        await api.post(content)   # ✅ async-safe
        print(f"[INFO] Posted: {title}")
    except Exception as e:
        print(f"[ERROR] Failed to post: {e}")

def job():
    asyncio.get_event_loop().run_until_complete(post_latest_news())

# Schedule every hour
schedule.every(1).hours.do(job)

print("[INFO] Auto Tech News Poster started...")

while True:
    schedule.run_pending()
    time.sleep(30)
