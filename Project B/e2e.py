import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to http://localhost:3000")
        await page.goto("http://localhost:3000")
        await page.wait_for_selector("text=URL Shortener")
        
        print("Taking initial screenshot...")
        await page.screenshot(path="screenshot-1-initial.png")
        
        print("Filling form...")
        await page.fill('input[type="url"]', "https://example.com/test-playwright-automation")
        await page.click('button[type="submit"]')
        
        print("Waiting for result...")
        await page.wait_for_selector("text=Short URL created!")
        await page.screenshot(path="screenshot-2-result.png")
        
        print("Switching to Dashboard...")
        await page.click("text=Dashboard")
        await page.wait_for_selector("text=1 URL in this session")
        
        print("Taking dashboard screenshot...")
        await page.screenshot(path="screenshot-3-dashboard.png")
        
        print("Success! Closing browser.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
