import os
import asyncio
from playwright.async_api import async_playwright

# --- Credentials (fallback defaults, but prefer GitHub Actions secrets) ---
USERNAME = os.getenv("THREADS_USERNAME", "thenajamburki")
PASSWORD = os.getenv("THREADS_PASSWORD", "Jeju12345@")

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

            # --- Username field ---
            print("[INFO] Finding username field...")
            username_selector = "input[name='username'], input[name='email'], input[name='usernameOrEmail'], input[type='text']"
            await page.wait_for_selector(username_selector, timeout=60000)
            await page.fill(username_selector, USERNAME)

            # --- Password field ---
            print("[INFO] Finding password field...")
            password_selector = "input[type='password']"
            await page.wait_for_selector(password_selector, timeout=30000)
            await page.fill(password_selector, PASSWORD)

            # --- Login button ---
            try:
                print("[INFO] Trying to click login button...")

                login_btn = None
                for locator in [
                    page.get_by_role("button", name="Log in"),
                    page.get_by_role("button", name="Log In"),
                    page.locator("button[type='submit']")
                ]:
                    if await locator.count() > 0:
                        login_btn = locator.first
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

            # --- Wait after login ---
            await page.wait_for_timeout(5000)

            # --- Verify login worked (check homepage composer) ---
            print("[INFO] Checking for composer after login...")
            if await page.locator("div[contenteditable='true']").count() == 0:
                await page.screenshot(path="login-failed.png")
                raise Exception("❌ Login failed. Screenshot saved → login-failed.png")

            print("[INFO] Logged in successfully ✅")

            # --- Example post ---
            post_text = "Whizz co-founder says Trump’s Chicago crackdown is scaring delivery workers off the streets\nRead more: https://techcrunch.com/"
            print(f"[INFO] Will post: {post_text[:80]}...")

            composer = page.locator("div[contenteditable='true']").first
            await composer.click()
            await composer.fill(post_text)

            # Click "Post"
            post_button = page.get_by_role("button", name="Post")
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
