from playwright.sync_api import sync_playwright
import time

def scrape_reuters_article(url):
    try:
        # Launch Playwright browser
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Set headless=False to see the browser
            time.sleep(2)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36" )  # Set user agent here on the context

            # Create a new page in the context
            page = context.new_page()

            # Navigate to the URL
            page.goto(url)

            page.screenshot(path="pain.png")
            # Extract the headline
            headline = page.locator('h1').text_content().strip()  # Extracting the main headline

            # Extract the article content (assuming it's within <div class="ArticleBody__content">)
            content = page.locator('.ArticleBody__content').text_content().strip()

            # Close the browser
            browser.close()

            return {
                "headline": headline,
                "content": content
            }
    except Exception as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    print("starting")
    url = "https://www.reuters.com/world/middle-east/iraqi-militias-enter-syria-reinforce-government-forces-military-sources-say-2024-12-02/"
    result = scrape_reuters_article(url)
    print(result)