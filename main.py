import asyncio
from playwright.async_api import async_playwright

USERNAME = "thenajamburki"
PASSWORD = "Jeju12345@"
POST_TEXT = "🚀 Auto-post test: Whizz co-founder says Trump’s Chicago crackdown is scaring delivery workers. Read more: https://techcrunch.com"

async def post_to_threads():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("[INFO] Navigating to Threads login...")
        await page.goto("https://www.threads.net/login", timeout=60000)

        # Login
        await page.fill("input[name='username']", USERNAME)
        await page.fill("input[name='password']", PASSWORD)
        await page.click("button[type='submit']")

        # Wait for feed/homepage to load
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path="after-login.png")
        print("[INFO] Logged in successfully (see after-login.png)")

        # Try to find composer
        try:
            await page.wait_for_selector("div[contenteditable='true']", timeout=20000)
            composer = await page.query_selector("div[contenteditable='true']")
        except Exception:
            await page.screenshot(path="no-composer.png")
            raise Exception("❌ Composer not found! Screenshot saved: no-composer.png")

        # Type post
        await composer.click()
        await composer.fill(POST_TEXT)

        # Find and click Post button
        try:
            await page.click("button:has-text('Post')")
        except Exception:
            await page.screenshot(path="post-btn-missing.png")
            raise Exception("❌ Post button not found! Screenshot saved: post-btn-missing.png")

        print("✅ Post submitted successfully!")
        await page.screenshot(path="after-post.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(post_to_threads())
