import os
import asyncio
from playwright.async_api import async_playwright

USERNAME = os.getenv("thenajamburki", "thenajamburki")
PASSWORD = os.getenv("Jeju12345@", "Jeju12345@")

THREADS_URL = "https://www.threads.net/login"

async def post_to_threads():
    async with async_playwright() as p:
        print("[INFO] Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print("[INFO] Navigating to Threads login...")
            await page.goto(THREADS_URL, timeout=60000)

            # Username
            print("[INFO] Finding username field...")
            username_selector = "input[name='username'], input[name='email'], input[type='text']"
            await page.wait_for_selector(username_selector, timeout=60000)
            await page.fill(username_selector, USERNAME)

            # Password
            print("[INFO] Finding password field...")
            password_selector = "input[type='password']"
            await page.wait_for_selector(password_selector, timeout=30000)
            await page.fill(password_selector, PASSWORD)

            # Login button
            print("[INFO] Trying to click login button...")
            login_btn = page.get_by_role("button", name="Log in").first
            await login_btn.click(timeout=15000)
            print("[INFO] Clicked login button ✅")

            # Debugging after login
            await page.wait_for_timeout(5000)
            print(f"[DEBUG] Current page: {await page.title()} → {page.url}")

            # Retry loop: check if logged in
            success = False
            for attempt in range(3):
                print(f"[INFO] Checking composer... attempt {attempt+1}/3")
                if await page.locator("div[contenteditable='true']").count() > 0 \
                   or await page.locator("textarea").count() > 0:
                    success = True
                    break
                await page.wait_for_timeout(5000)

            if not success:
                await page.screenshot(path="login-failed.png")
                raise Exception("❌ Login failed. Screenshot saved → login-failed.png")

            print("[INFO] Logged in successfully ✅")

            # Post
            post_text = "Whizz co-founder says Trump’s Chicago crackdown is scaring delivery workers off the streets\nRead more: https://techcrunch.com/"
            composer = page.locator("div[contenteditable='true'], textarea").first
            await composer.click()
            await composer.fill(post_text)

            post_button = page.get_by_role("button", name="Post").first
            await post_button.click(timeout=10000)

            print("[INFO] Post submitted ✅")
            await page.screenshot(path="after-post.png")

        except Exception as e:
            print(f"[FATAL] {e}")
            await page.screenshot(path="fatal-error.png")
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(post_to_threads())
