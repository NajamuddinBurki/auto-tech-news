import asyncio
import json
import os
from playwright.async_api import async_playwright

THREADS_USERNAME = os.getenv("THREADS_USERNAME")
THREADS_PASSWORD = os.getenv("THREADS_PASSWORD")

COOKIES_FILE = "cookies.json"


async def post_to_threads():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120 Safari/537.36"
        )
        page = await context.new_page()
        page.set_default_timeout(60000)  # 60s for safety

        # --- Try loading cookies ---
        if os.path.exists(COOKIES_FILE):
            try:
                cookies = json.load(open(COOKIES_FILE))
                await context.add_cookies(cookies)
                print("[INFO] Loaded cookies → trying session restore")
                await page.goto("https://www.threads.net/", wait_until="domcontentloaded")
                await page.wait_for_timeout(5000)
                if "login" not in page.url:
                    print("[INFO] ✅ Session restored successfully")
                    # TODO: replace with actual posting logic
                    await browser.close()
                    return
                else:
                    print("[INFO] Session expired → doing fresh login")
            except Exception as e:
                print(f"[WARN] Failed to load cookies: {e}")

        # --- Fresh Login ---
        print("[INFO] Navigating to Threads login...")
        await page.goto("https://www.threads.net/login", wait_until="domcontentloaded")
        await page.screenshot(path="before-login.png", full_page=True)

        try:
            username_selector = "input[name='username'], input[name='email'], input[name='usernameOrEmail']"
            password_selector = "input[name='password']"

            await page.wait_for_selector(username_selector, timeout=60000)
            username_field = await page.query_selector(username_selector)
            password_field = await page.query_selector(password_selector)

            await username_field.fill(THREADS_USERNAME)
            await password_field.fill(THREADS_PASSWORD)
            await password_field.press("Enter")

            print("[INFO] Submitted login form...")
            await page.wait_for_timeout(8000)

            # Save cookies for next time
            cookies = await context.cookies()
            json.dump(cookies, open(COOKIES_FILE, "w"))
            print("[INFO] ✅ Login successful → cookies saved")

        except Exception as e:
            await page.screenshot(path="login-failed.png", full_page=True)
            raise Exception("❌ Login failed. Screenshot saved → login-failed.png") from e

        # --- Example posting flow ---
        try:
            print("[INFO] Navigating to posting area...")
            await page.goto("https://www.threads.net/", wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)

            # Example post text
            content = "🚀 Hello Threads! Automated post via Playwright."

            # Find text area (selector may change, adjust if needed)
            await page.click("div[role='textbox']")
            await page.keyboard.type(content)
            await page.wait_for_timeout(2000)

            # Submit post button (selector may vary)
            await page.click("text=Post")

            print("[INFO] ✅ Post submitted successfully")

        except Exception as e:
            await page.screenshot(path="post-failed.png", full_page=True)
            raise Exception("❌ Post failed. Screenshot saved → post-failed.png") from e

        await browser.close()


if __name__ == "__main__":
    asyncio.run(post_to_threads())
