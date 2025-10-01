import sys
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")

try:
    # Preferred import (PyPI packaged version)
    from threads_api import ThreadsAPI
    logging.info("✅ Imported ThreadsAPI (top-level)")
except ImportError:
    try:
        # Fallback for source structure
        from threads_api.src.threads_api import ThreadsAPI
        logging.info("✅ Imported ThreadsAPI (src fallback)")
    except ImportError as e:
        logging.error("❌ Cannot import ThreadsAPI. Check threads_api install.")
        sys.exit(1)


# ---------------------------
# Config (Secrets stored in GH Actions env vars)
# ---------------------------
import os

USERNAME = os.getenv("THREADS_USERNAME")
PASSWORD = os.getenv("THREADS_PASSWORD")

if not USERNAME or not PASSWORD:
    logging.error("❌ Missing THREADS_USERNAME or THREADS_PASSWORD env vars.")
    sys.exit(1)


# ---------------------------
# API Init (adjust to current threads_api)
# ---------------------------
try:
    api = ThreadsAPI()
    api.login(USERNAME, PASSWORD)
    logging.info("✅ Logged into Threads API")
except Exception as e:
    logging.error(f"❌ Login failed: {e}")
    sys.exit(1)


# ---------------------------
# Example post
# ---------------------------
try:
    post_id = api.publish("🚀 Auto post test from GitHub Actions")
    logging.info(f"✅ Post published successfully (ID: {post_id})")
except Exception as e:
    logging.error(f"❌ Error posting: {e}")
    sys.exit(1)
