from playwright.sync_api import sync_playwright, Playwright
from playwright_stealth import stealth_sync
import time
def run(playwright: Playwright):
    chromium = playwright.chromium # or "firefox" or "webkit".
    browser = chromium.launch()
    page = browser.new_page()
    stealth_sync(page)
    page.set_extra_http_headers({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    });
    page.goto("https://www.allsides.com/login")
    page.evaluate("window.scrollBy(0, 500)")
    time.sleep(2)
    #page.get_by_role('button', name='Verify you are human').click()
    page.screenshot(path="first.png")
    #return
    page.get_by_label('Email address or username').fill('sensemaking')
    time.sleep(1)
    page.get_by_label('password').fill('sensemaking123')
    time.sleep(1)
    page.get_by_role('button', name='Log In').click()
    time.sleep(1)
    page.screenshot(path="example.png")
    page.evaluate("window.scrollBy(0, 500)")
    return
    page.goto("https://www.allsides.com/bias-checker")
    time.sleep(1)
    page.get_by_role('button', name='Agree').click()
    time.sleep(1)
    page.screenshot(path="example2.png")
    # other actions...
    browser.close()

with sync_playwright() as playwright:
    run(playwright)