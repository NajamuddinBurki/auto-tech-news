import os
import asyncio
from playwright.async_api import async_playwright

# --- Credentials ---
USERNAME = os.getenv("thenajamburki", "thenajamburki")
PASSWORD = os.getenv("Jeju12345@", "Jeju12345@")

POST_TEXT = "Whizz co-founder says Trump’s Chicago crackdown is scaring delivery workers off the streets  Read more: https://techcrunch.com"

async def post_to_threads():
    async with async_playwright() as p:
        print("[INFO] Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("[INFO] Navigating to Threads login...")
        await page.goto("https://www.threads.net/login", timeout=60000)

        # --- Username field ---
        print("[INFO] Finding username field...")
        await page.fill("input[type='text']", USERNAME)

        # --- Password field ---
        print("[INFO] Finding password field...")
        await page.fill("//input[@type='password']", PASSWORD)

        # --- FIXED Login Button Click ---
        try:
            print("[INFO] Trying to click login button...")

            login_btn = None
            for selector in [
                "button[type='submit']",
                "text='Log in'",
                "text='Log In'"
            ]:
                locator = page.locator(selector)
                if await locator.count() > 0:
                    login_btn = locator
                    break

            if login_btn:
                await login_btn.click(timeout=10000)
                print("[INFO] Clicked login button ✅")
            else:
                raise Exception("❌ Login button not found on page.")

        except Exception as e:
            await page.screenshot(path="debug-login-error.png")
            print(f"[ERROR] Login button issue: {e}")
            raise

        # --- Wait for homepage load ---
        await page.wait_for_timeout(5000)

        # --- Try to find composer ---
        try:
            print("[INFO] Locating composer...")
            composer = page.locator("textarea, div[contenteditable='true']")
            if await composer.count() == 0:
                raise Exception("Composer not found")

            await composer.first.click()
            await composer.first.fill(POST_TEXT)

            print("[INFO] Clicking Post button...")
            await page.click("text=Post", timeout=10000)
            print("[INFO] Post submitted ✅")

        except Exception as e:
            await page.screenshot(path="debug-post-error.png")
            html = await page.content()
            with open("page-source.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[ERROR] Posting failed: {e}")
            raise

        await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(post_to_threads())
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
