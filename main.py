# main.py
# Playwright-driven single-run Threads poster (posts one TechCrunch headline, then exits).
# Requires: playwright, feedparser
# Environment variables required (set in workflow or export locally):
#   THREADS_USERNAME, THREADS_PASSWORD

import os
import sys
import time
import random
import feedparser
import traceback
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

# ---------- Config ----------
RSS_FEED = "https://techcrunch.com/feed/"
# Post template: tune this to your style
POST_TEMPLATE = "{title}\n\nRead more: {link}\n\n#TechNews #TechCrunch"
# ---------- End Config ----------

USERNAME = os.getenv("THREADS_USERNAME")
PASSWORD = os.getenv("THREADS_PASSWORD")

if not USERNAME or not PASSWORD:
    print("[ERROR] THREADS_USERNAME or THREADS_PASSWORD not set in environment. Exit.")
    sys.exit(1)

def fetch_headlines(max_items=5):
    feed = feedparser.parse(RSS_FEED)
    if not getattr(feed, "entries", None):
        return []
    return feed.entries[:max_items]

def safe_find_and_fill(page, selectors, value, timeout=2500):
    for sel in selectors:
        try:
            el = page.wait_for_selector(sel, timeout=timeout)
            if el:
                try:
                    el.fill(value, timeout=2000)
                except Exception:
                    # If it's not fillable (contenteditable), click + type
                    el.click(timeout=2000)
                    page.keyboard.type(value, delay=10)
                return True
        except PWTimeoutError:
            continue
    return False

def safe_click(page, selectors, timeout=3000):
    for sel in selectors:
        try:
            btn = page.wait_for_selector(sel, timeout=timeout)
            if btn:
                try:
                    btn.click(timeout=3000)
                except Exception:
                    page.evaluate("(el) => el.click()", btn)
                return True
        except PWTimeoutError:
            continue
    return False

def login_and_post(post_text, headless=True):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless, args=["--no-sandbox"])
            context = browser.new_context()
            page = context.new_page()

            # Try direct login page
            login_url = "https://www.threads.net/login"
            page.goto(login_url, timeout=60000)

            # username selectors
            username_selectors = [
                "input[name='username']",
                "input[name='email']",
                "input[aria-label*='email']",
                "input[placeholder*='email']",
                "input[placeholder*='username']",
                "input[type='text']"
            ]
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[aria-label*='password']",
                "input[placeholder*='Password']"
            ]
            filled_user = safe_find_and_fill(page, username_selectors, USERNAME)
            filled_pass = safe_find_and_fill(page, password_selectors, PASSWORD)

            if not (filled_user and filled_pass):
                # fallback: try Instagram-style flow (some accounts redirect)
                print("[WARN] Couldn't find standard login inputs; trying alternative flow.")
                # try to click any login button to open form
                alt_login_btns = ["button:has-text('Log in')", "button:has-text('Sign in')", "a:has-text('Log in')"]
                safe_click(page, alt_login_btns)
                # try again after opening
                filled_user = safe_find_and_fill(page, username_selectors, USERNAME, timeout=4000)
                filled_pass = safe_find_and_fill(page, password_selectors, PASSWORD, timeout=4000)

            if not (filled_user and filled_pass):
                print("[ERROR] Unable to locate username/password inputs. Stop.")
                # Save screenshot for debugging
                try:
                    page.screenshot(path="login-page.png", full_page=True)
                    print("[DEBUG] Saved login-page.png")
                except Exception:
                    pass
                browser.close()
                return False

            # submit button
            submit_selectors = [
                "button[type='submit']",
                "button:has-text('Log in')",
                "button:has-text('Log In')",
                "button:has-text('Continue')",
                "button:has-text('Sign in')"
            ]
            clicked = safe_click(page, submit_selectors)
            # wait for navigation or composer
            try:
                # wait for either redirect or composer availability
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass

            # After login, go to home which contains composer
            page.goto("https://www.threads.net/", timeout=60000)

            # Wait a short time for UI to render
            time.sleep(2)

            # Composer selectors (many UI variants)
            composer_selectors = [
                "div[role='textbox']",
                "div[contenteditable='true']",
                "textarea",
                "div[aria-label*='Create']",
                "div[aria-label*='new thread']"
            ]
            composer_found = None
            for sel in composer_selectors:
                try:
                    el = page.query_selector(sel)
                    if el:
                        composer_found = sel
                        break
                except Exception:
                    continue

            if not composer_found:
                print("[ERROR] Composer not found on Threads homepage. Dumping page HTML for debug.")
                try:
                    html = page.content()
                    with open("page-source.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    print("[DEBUG] saved page-source.html")
                except Exception:
                    pass
                browser.close()
                return False

            # Fill composer
            try:
                if composer_found in ("textarea", "input", "div[role='textbox']", "div[contenteditable='true']"):
                    el = page.query_selector(composer_found)
                    el.click()
                    # For contenteditable, use keyboard
                    page.keyboard.type(post_text, delay=5)
                else:
                    # fallback fill
                    page.fill(composer_found, post_text)
            except Exception:
                # fallback try typing into focused element
                page.keyboard.type(post_text, delay=5)

            # Find "Post" / "Share" button
            post_buttons = [
                "button:has-text('Post')",
                "button:has-text('Share')",
                "button:has-text('Publish')",
                "div[role='button'] >> text='Post'"
            ]
            posted = safe_click(page, post_buttons)
            if not posted:
                # alternative attempt: press Ctrl+Enter
                try:
                    page.keyboard.down("Control")
                    page.keyboard.press("Enter")
                    page.keyboard.up("Control")
                    time.sleep(2)
                except Exception:
                    pass

            # Wait a bit and check for success
            time.sleep(3)
            print("[INFO] Attempted to post. Check Threads to confirm.")
            # Optional: save screenshot
            try:
                page.screenshot(path="after-post.png", full_page=False)
                print("[DEBUG] Saved after-post.png")
            except Exception:
                pass

            browser.close()
            return True

    except Exception as exc:
        print("[ERROR] Unexpected exception during login_and_post:")
        traceback.print_exc()
        try:
            with open("pw-exception.txt", "w") as f:
                f.write(str(exc))
        except Exception:
            pass
        return False

def main():
    headlines = fetch_headlines(8)
    if not headlines:
        print("[ERROR] No headlines fetched from feed. Exiting.")
        sys.exit(1)

    # pick the freshest or random headline
    entry = headlines[0]  # top item (freshest)
    title = getattr(entry, "title", "")
    link = getattr(entry, "link", "")
    post_text = POST_TEMPLATE.format(title=title.strip(), link=link.strip())

    print("[INFO] Will post:", post_text[:120].replace("\n", " ") + "...")
    ok = login_and_post(post_text, headless=True)
    if not ok:
        print("[ERROR] Posting failed. See debug files (login-page.png, page-source.html, after-post.png) if created.")
        sys.exit(2)
    print("[INFO] Done.")
    sys.exit(0)

if __name__ == "__main__":
    main()
