from bs4 import BeautifulSoup
import requests
from url_to_html import url
# import lxml

def clean_html_preserve_structure(html_content):
    """
    HTML 콘텐츠를 정제하여 스타일 및 장식적인 태그와 관련 속성만 제거하고,
    구조적인 태그는 그대로 유지합니다.
    
    Args:
        html_content (str): 정제할 HTML 콘텐츠
    
    Returns:
        str: 정제된 HTML 콘텐츠
    """
    # BeautifulSoup 객체 생성 (lxml 파서 사용)
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 제거할 태그 리스트 (스타일 및 장식적인 태그)
    tags_to_remove = ['style', 'script', 'aside', 'nav', 'footer', 'header', 'iframe', 'noscript', 'form']
    
    for tag in tags_to_remove:
        for element in soup.find_all(tag):
            element.decompose()  # 태그와 그 내용을 완전히 제거
    
    # 제거할 속성 리스트 (스타일 관련 속성)
    attributes_to_remove = ['style', 'class', 'id']
    
    for tag in soup.find_all(True):  # 모든 태그 순회
        for attr in attributes_to_remove:
            if attr in tag.attrs:
                del tag.attrs[attr]
    
    # 정제된 HTML 문자열 반환
    cleaned_html = str(soup)
    return cleaned_html

if __name__ == "__main__":

# 변수 html_content 에 직접 html넣는 방법 찾기
    response = requests.get(url)
    html_content = response.text
    cleaned_html = clean_html_preserve_structure(html_content)
    print(cleaned_html)
