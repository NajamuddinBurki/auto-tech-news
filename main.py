import asyncio, json, os
from playwright.async_api import async_playwright

USERNAME = os.getenv("thenajamburki", "thenajamburki")
PASSWORD = os.getenv("Jeju12345@", "Jeju12345@")
COOKIES_FILE = "cookies.json"

POST_TEXT = "🚀 Auto-post test: Whizz co-founder says Trump’s Chicago crackdown is scaring delivery workers. Read more: https://techcrunch.com"


async def save_cookies(context):
    cookies = await context.cookies()
    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f)


async def load_cookies(context):
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "r") as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        return True
    return False


async def post_to_threads():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Try cookie-based login first
        used_cookies = await load_cookies(context)
        page = await context.new_page()
        await page.goto("https://www.threads.net", timeout=60000)

        if not used_cookies:
            print("[INFO] No cookies found → doing login")
            await page.goto("https://www.threads.net/login", timeout=60000)

            # Handle redirect button if present
            try:
                if await page.query_selector("text=Log in with Instagram"):
                    await page.click("text=Log in with Instagram")
            except:
                pass

            # Wait for username field
            try:
                await page.wait_for_selector("input[name='username']", timeout=20000)
                await page.fill("input[name='username']", USERNAME)
                await page.fill("input[name='password']", PASSWORD)
                await page.click("button[type='submit']")
            except Exception as e:
                await page.screenshot(path="login-failed.png")
                raise Exception("❌ Login failed. See login-failed.png") from e

            # Save cookies for reuse
            await page.wait_for_load_state("networkidle")
            await save_cookies(context)
            await page.screenshot(path="after-login.png")
            print("[INFO] Logged in successfully (cookies saved).")

        else:
            print("[INFO] Logged in with cookies.")

        # Navigate to home
        await page.goto("https://www.threads.net", timeout=60000)
        await page.wait_for_load_state("networkidle")

        # Find composer (multiple fallback selectors)
        composer = None
        for selector in [
            "div[contenteditable='true']",
            "textarea",
            "div[role='textbox']",
            "div[aria-label='Start a thread']"
        ]:
            try:
                composer = await page.wait_for_selector(selector, timeout=10000)
                if composer:
                    break
            except:
                continue

        if not composer:
            await page.screenshot(path="no-composer.png")
            raise Exception("❌ Composer not found. See no-composer.png")

        await composer.click()
        await composer.fill(POST_TEXT)

        # Post button (fallbacks)
        posted = False
        for btn_selector in [
            "button:has-text('Post')",
            "button:has-text('Share')",
            "button >> nth=0"  # fallback: first button
        ]:
            try:
                await page.click(btn_selector, timeout=5000)
                posted = True
                break
            except:
                continue

        if not posted:
            await page.screenshot(path="post-btn-missing.png")
            raise Exception("❌ Post button not found. See post-btn-missing.png")

        print("✅ Post submitted successfully!")
        await page.screenshot(path="after-post.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(post_to_threads())
