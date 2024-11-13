
from url_to_html import url
from goose3 import Goose

# 기사 URL

# Goose 객체 생성
g = Goose()

# 기사 추출
article = g.extract(url=url)

# 추출된 정보 출력
print("제목:", article.title)
print("저자:", article.authors)
print("발행 날짜:", article.publish_date)
print("본문:", article.cleaned_text)
print("이미지 URL:", article.top_image.src if article.top_image else 'No image')
