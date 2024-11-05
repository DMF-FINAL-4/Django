from url_to_html import url
import trafilatura
from trafilatura.settings import use_config

# 사용자 정의 설정
config = use_config()
config.set("DEFAULT", "EXTRACTION_TIMEOUT", "10")
config.set("DEFAULT", "STRICT_EXTRACTION", "True")

# 기사 URL

# URL에서 콘텐츠 다운로드
downloaded = trafilatura.fetch_url(url, config=config)

# 콘텐츠 추출
text = trafilatura.extract(downloaded, config=config)

print("본문:", text)
