import os
from url_to_html import url
import asyncio
from pyppeteer import launch

async def take_screenshot(url, output_path):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.goto(url)
    await page.screenshot({'path': output_path})
    await browser.close()

# 사용 예시
output_path = 'C:/webdrivers/screenshot_path/screenshot.png'
asyncio.get_event_loop().run_until_complete(take_screenshot(url, output_path))

print(f"스크린샷이 '{output_path}'로 저장되었습니다.")
