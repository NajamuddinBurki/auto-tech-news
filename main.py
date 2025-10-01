import asyncio
import feedparser
import schedule
import time
import os
from threads_api import ThreadsAPI  # ✅ Official import from PyPI

# ===============================
# 🔧 Configuration (env variables)
# ===============================
USERNAME = os.getenv("THREADS_USERNAME")
PASSWORD = os.getenv("THREADS_PASSWORD")
RSS_FEED = "https://techcrunch.com/feed/"  # Replace with your RSS feed

# ===============================
# 🔧 Setup Asyncio + API
# ===============================
# Ensure event loop exists (for GitHub Actions / runners)
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

api = ThreadsAPI()

# ===============================
# 🔧 Login
# ===============================
async def login():
    """Login to Threads API."""
    try:
        await api.login(USERNAME, PASSWORD)
        print("[INFO] Logged in successfully ✅")
    except Exception as e:
        print(f"[ERROR] Login failed ❌: {e}")
        raise

# Run login once at startup
asyncio.get_event_loop().run_until_complete(login())

# ===============================
# 🔧 Post Latest News
# ===============================
async def post_latest_news():
    """Fetch latest news from RSS feed and post to Threads."""
    try:
        feed = feedparser.parse(RSS_FEED)
        if not feed.entries:
            print("[WARN] No entries found in RSS feed ⚠️")
            return

        latest = feed.entries[0]
        title = latest.title
        link = latest.link
        content = f"{title}\n\nRead more: {link}"

        await api.post(content)
        print(f"[INFO] Posted: {title} 🚀")

    except Exception as e:
        print(f"[ERROR] Failed to post ❌: {e}")

# ===============================
# 🔧 Scheduled Job
# ===============================
def job():
    """Run the posting job inside asyncio loop."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(post_latest_news())

# Post every 1 hour
schedule.every(1).hours.do(job)

print("[INFO] Auto Tech News Poster started... ⏳")

# ===============================
# 🔧 Main Loop
# ===============================
while True:
    schedule.run_pending()
    time.sleep(30)
