from bs4 import BeautifulSoup
import requests
from url_to_html import url
import re

# HTML 콘텐츠에서 필요한 태그만 남기는 함수 정의
def clean_html_content(html_content):
    """
    HTML 콘텐츠에서 필요한 태그만 남기고 나머지를 제거하여 정제된 HTML을 반환합니다.
    
    Args:
        html_content (str): HTML 콘텐츠
    
    Returns:
        str: 정제된 HTML 콘텐츠
    """
    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 필요한 태그 리스트 (중요 정보가 포함된 태그들)
    tags_to_keep = ['meta', 'title', 'article', 'section', 'p', 'div', 'span', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    
    # 모든 태그 순회하면서 필요한 태그가 아니면 제거
    for tag in soup.find_all(True):
        if tag.name not in tags_to_keep:
            tag.decompose()
    
    # 한글 또는 영문이 포함되지 않은 태그 제거
    for tag in soup.find_all(True):
        if not re.search(r'[가-힣a-zA-Z]', tag.get_text(strip=True)):
            tag.decompose()
    
    # 모든 태그에서 제거할 속성 리스트 (스타일 관련 속성)
    attributes_to_remove = ['style', 'class', 'id', 'data-*']
    
    for tag in soup.find_all(True):  # 모든 태그 순회
        for attr in list(tag.attrs):
            if attr in attributes_to_remove or attr.startswith('data-'):
                del tag.attrs[attr]
    
    # 정제된 HTML 문자열 반환
    cleaned_html = str(soup)
    return cleaned_html

if __name__ == "__main__":
    # 웹 페이지 요청 및 HTML 콘텐츠 가져오기
    response = requests.get(url)
    html_content = response.text
    
    # 필요한 태그만 남기기
    cleaned_html = clean_html_content(html_content)
    
    # 정제된 HTML 출력
    if cleaned_html.strip():
        print(cleaned_html)
    else:
        print("No relevant content found.")