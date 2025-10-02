import os
import asyncio
from playwright.async_api import async_playwright

# ✅ Hardcoded fallback credentials (use GitHub secrets in production!)
USERNAME = os.getenv("THREADS_USERNAME", "thenajamburki")
PASSWORD = os.getenv("THREADS_PASSWORD", "Jeju12345@")

async def post_to_threads():
    async with async_playwright() as p:
        print("[INFO] Launching browser... headless=True")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("[INFO] Navigating to Threads login...")
        await page.goto("https://www.threads.net/login", timeout=60000)

        try:
            print("[INFO] Finding username field...")
            await page.wait_for_selector("input[aria-label='Phone number, username, or email']", timeout=20000)
            await page.fill("input[aria-label='Phone number, username, or email']", USERNAME)

            print("[INFO] Finding password field...")
            await page.wait_for_selector("input[aria-label='Password']", timeout=20000)
            await page.fill("input[aria-label='Password']", PASSWORD)

            print("[INFO] Clicking login button...")
            await page.click("button[type='submit']")
            await page.wait_for_timeout(5000)  # wait for login redirect

            # Check if login succeeded by looking for the composer
            print("[INFO] Checking for composer after login...")
            if await page.query_selector("div[role='textbox']") is None:
                await page.screenshot(path="login-failed.png")
                raise Exception("❌ Login failed. Screenshot saved → login-failed.png")

            print("[INFO] Login successful ✅")
            # Example post
            await page.fill("div[role='textbox']", "🚀 Auto-post test from Playwright bot!")
            await page.click("text=Post")

            print("[INFO] Post submitted successfully ✅")

        except Exception as e:
            await page.screenshot(path="fatal-error.png")
            print(f"[FATAL] {e}")
            raise

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(post_to_threads())
