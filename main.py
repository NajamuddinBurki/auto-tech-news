import os
import asyncio
from playwright.async_api import async_playwright

USERNAME = os.getenv("THREADS_USERNAME", "thenajamburki")
PASSWORD = os.getenv("THREADS_PASSWORD", "Jeju12345@")


async def post_to_threads():
    async with async_playwright() as p:
        # Detect if running inside GitHub Actions (CI)
        in_ci = os.getenv("GITHUB_ACTIONS") == "true"
        headless_mode = True if in_ci else False

        print(f"[INFO] Launching browser... headless={headless_mode}")
        browser = await p.chromium.launch(headless=headless_mode)

        context = await browser.new_context()
        page = await context.new_page()

        print("[INFO] Navigating to Threads login...")
        await page.goto("https://www.threads.net/login")

        # Username
        print("[INFO] Finding username field...")
        await page.fill("input[type='text']", USERNAME)

        # Password
        print("[INFO] Finding password field...")
        await page.fill("input[type='password']", PASSWORD)

        # Click login
        print("[INFO] Trying to click login button...")
        try:
            await page.get_by_role("button", name="Log in").click(timeout=10000)
            print("[INFO] Clicked login button ✅")
        except Exception as e:
            await page.screenshot(path="login-error.png")
            raise Exception(f"❌ Login button issue: {e}")

        # Wait after login
        print("[INFO] Checking for composer after login...")
        try:
            await page.wait_for_selector("div[role='textbox']", timeout=15000)
            print("[INFO] ✅ Logged in successfully!")
        except:
            await page.screenshot(path="login-failed.png")
            raise Exception("❌ Login failed. Screenshot saved → login-failed.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(post_to_threads())
