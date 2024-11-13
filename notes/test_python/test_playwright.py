from url_to_html import url
import asyncio
from playwright.async_api import async_playwright

async def take_screenshot_async(url, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.screenshot(path=output_path)
        await browser.close()

# 사용 예시
if __name__ == "__main__":
    # url = 'https://example.com'
    output_path = 'C:/webdrivers/screenshot_path/screenshot.png'
    asyncio.run(take_screenshot_async(url, output_path))
    print(f"스크린샷이 '{output_path}'로 저장되었습니다.")
