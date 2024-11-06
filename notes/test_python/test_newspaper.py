from url_to_html import url
from newspaper import Article

# 기사 URL

# Article 객체 생성 (언어 설정)
article = Article(url, language='ko')

# 기사 다운로드
article.download()

# 파싱
article.parse()

# 추출된 정보 출력
print("제목:", article.title)
print("저자:", article.authors)
print("발행 날짜:", article.publish_date)
print("본문:", article.text)
print("키워드:", article.keywords)
