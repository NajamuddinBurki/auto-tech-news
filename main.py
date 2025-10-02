import os
import asyncio
from playwright.async_api import async_playwright

# Hardcoded fallback (you asked me to keep them here)
USERNAME = os.getenv("THREADS_USERNAME", "thenajamburki")
PASSWORD = os.getenv("THREADS_PASSWORD", "Jeju12345@")

POST_TEXT = "🚀 Auto-post test from GitHub Actions!"

async def post_to_threads():
    async with async_playwright() as p:
        print("[INFO] Launching browser... headless=True")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("[INFO] Navigating to Threads login...")
        await page.goto("https://www.threads.net/login", wait_until="networkidle")

        # --- ⚡ Handle Instagram iframe login ---
        print("[INFO] Waiting for Instagram login iframe...")
        iframe_element = await page.wait_for_selector("iframe[src*='instagram.com']", timeout=30000)
        frame = await iframe_element.content_frame()

        if not frame:
            raise Exception("❌ Could not switch into Instagram login iframe.")

        print("[INFO] Filling username...")
        await frame.fill("input[name='username']", USERNAME)
        print("[INFO] Filling password...")
        await frame.fill("input[name='password']", PASSWORD)

        print("[INFO] Clicking login button...")
        await frame.click("button[type='submit']", timeout=10000)

        # --- ⚡ Verify login success ---
        try:
            await page.wait_for_selector("div[role='textbox']", timeout=20000)
            print("[SUCCESS] Logged in successfully ✅")
        except Exception:
            await page.screenshot(path="login-failed.png")
            raise Exception("❌ Login failed. Screenshot saved → login-failed.png")

        # --- ⚡ Post content ---
        print("[INFO] Looking for composer...")
        await page.click("div[role='textbox']", timeout=10000)
        await page.keyboard.type(POST_TEXT)

        print("[INFO] Clicking post button...")
        await page.click("button:has-text('Post')", timeout=10000)

        print("[SUCCESS] Post created successfully ✅")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(post_to_threads())
