import asyncio
from playwright.async_api import async_playwright
import os

# Credentials with env override
USERNAME = os.getenv("thenajamburki", "thenajamburki")
PASSWORD = os.getenv("Jeju12345@", "Jeju12345@")
THREADS_URL = "https://www.threads.net/login"

async def post_to_threads():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("[INFO] Navigating to Threads login...")
        await page.goto(THREADS_URL, timeout=60000)

        # Save debug info
        await page.screenshot(path="debug-login-page.png", full_page=True)
        html = await page.content()
        with open("debug-login-page.html", "w", encoding="utf-8") as f:
            f.write(html)

        # Try multiple login field selectors
        username_selectors = [
            "input[name='username']",
            "input[name='email']",
            "input[name='usernameOrEmail']",
            "input[name='usernameOrPhone']",
            "input[type='text']",
            "//input[contains(@aria-label, 'Phone') or contains(@aria-label, 'Email')]",
            "//input[@autocomplete='username']"
        ]
        password_selectors = [
            "input[name='password']",
            "//input[@type='password']"
        ]

        username_box = None
        for sel in username_selectors:
            try:
                username_box = await page.wait_for_selector(sel, timeout=5000)
                if username_box:
                    print(f"[INFO] Found username field with selector: {sel}")
                    break
            except:
                continue

        if not username_box:
            raise Exception("❌ Could not find username field. Check debug-login-page.png & debug-login-page.html")

        await username_box.fill(USERNAME)

        # Find password field
        password_box = None
        for sel in password_selectors:
            try:
                password_box = await page.wait_for_selector(sel, timeout=5000)
                if password_box:
                    print(f"[INFO] Found password field with selector: {sel}")
                    break
            except:
                continue

        if not password_box:
            raise Exception("❌ Could not find password field. Check debug-login-page.png & debug-login-page.html")

        await password_box.fill(PASSWORD)

        # Click login button
        try:
            await page.click("button[type='submit'], text=Log in, text=Log In", timeout=10000)
        except:
            raise Exception("❌ Could not find login button.")

        print("[INFO] Login submitted. Waiting for homepage...")
        await page.wait_for_timeout(10000)
        await page.screenshot(path="after-login.png", full_page=True)

        # Continue posting logic here...
        print("[INFO] Login successful!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(post_to_threads())
