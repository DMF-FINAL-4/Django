from url_to_html import url

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Chrome 옵션 설정 (Headless 모드)
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
# chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (Windows 환경에서 필요할 수 있음)

# ChromeDriver 경로 설정
service = Service('C:/webdrivers/chrome-win64/chrome.exe')
# 웹 드라이버 초기화
driver = webdriver.Chrome(service=service, options=chrome_options)

# 특정 URL로 이동
driver.get(url)

# 스크린샷 저장
screenshot_path = 'C:/webdrivers/screenshot_path/screenshot.png'
driver.save_screenshot('screenshot.png')

# 브라우저 종료
driver.quit()

print("스크린샷이 'screenshot.png'로 저장되었습니다.")
