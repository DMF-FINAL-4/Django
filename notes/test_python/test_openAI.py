import os
import argparse
import openai
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup

def extract_information_with_gpt(cleaned_html, api_key):
    """
    정제된 HTML을 OpenAI GPT에게 전달하여 특정 정보를 추출합니다.

    Args:
        cleaned_html (str): 정제된 HTML 콘텐츠
        api_key (str): OpenAI API 키

    Returns:
        dict: GPT가 추출한 정보
    """
    openai.api_key = api_key

    prompt = f"""
    아래는 정제된 웹 페이지의 HTML입니다. 이 HTML에서 다음 정보를 추출하여 JSON 형식으로 반환하세요:
    - 접근권한 (access_permission) : 만약 접근에 제한이 있는 페이지로 확인된다면 'HTTP 상태 코드', '없는 페이지', '로그인 필요' 등의 적절한 항목을 출력. 문제가 없다면 '정상'을 출력
    - 파비콘(favicon) : 파비콘의 호스트 도메인을 포함한 전체 경로를 저장, 민약 여러개라면 가장 큰 이미지의 것을 1개만 저장
    - 호스트 도메인 (host_domain) :
    - 호스트 이름 (host_name) : 호스트의 이름을 한글로 출력, 한글이 없다면 영어로 출력 (예시: 네이버 뉴스, 페이스북, 위키백과)
    - 대체 url (alternate_url) : Canonical URL 또는 Open Graph URL이 존재 한다면 이곳에 표시
    - 제목 (title) : 각종 정보를 종합한 제목 (예시: '동아일보｜[이철희 칼럼] 형제애로 마련한 400억…감사 전한 튀르키예')
    - 작성자 (author) : 본문의 작성자
    - 작성일 (date) : 페이지의 작성일
    - 본문 (content) : 명백한 오타 수정을 제외한 텍스트 외곡이 없으며, 표 내부의 내용 등을 포함한 누락 없는 본문
    - 짧은 요약 (short_summary) : 본문을 20자에서 90자로 사이로 요약
    - 긴 요약 (long_summary) : 본문을 200자에서 400자 사이로 요약
    - 키워드 (keywords) : 본문의 키워드들 내용이 길고 요소가 많다면 키워드들이 아주 많아져도 좋아
    - 유형 키워드 (category_keywords) : 블로그, 카페, 기사, 정보, 사연, 에세이, 영상, 사진, 리뷰, 쇼핑, sns 등 유형이라 할 수 있는 키워드들 풍부하게
    - 댓글 (comments) : 댓글이 있다면 '작성자 | 댓글내용 | 작성시간' 형식으로 저장
    - 이미지 링크 (image_links) : 주요 이미지들의 링크 주소 {{"이미지캡션" : "이미지링크url"}} 딕셔너리 형식으로 저장
    - 링크(links) : 본문 내에 주요한 외부 또는 내부 링크들이 있을경우 {{"캡션" : "링크url"}} 딕셔너리 형식으로 저장
    - 비디오 및 오디오(media) : 본문 내에 미디어가 있을경우 {{"캡션" : "링크url"}} 딕셔너리 형식으로 저장
    - 파일 다운로드 링크(file_download_links) : 주요한 PDF, 이미지, 문서 등의 다운로드 링크가 있을경우 {{"파일제목 | 파일 크기": "링크url"}} 딕셔너리 형식으로 저장
    - 콘텐츠의 길이(content_length) : 콘텐츠를 읽는데 걸리는 시간을 예측 1분 단위로



    HTML:
    \"\"\"
    {cleaned_html}
    \"\"\"

    JSON 형식 예시:
    {{
        "access_permission": "정상",
        "favicon" : "https://www.example.com/favicon.ico"
        "host_domain": "example.com",
        "host_name": "네이버 뉴스",
        "alternate_url": "https://www.example.com/page-url",
        "title": "제목",
        "author": "작성자",
        "date": "YYYY-MM-DD",
        "content": "본문 내용",
        "short_summary": "본문을 20자에서 90자로 요약한 내용",
        "long_summary": "본문을 200자에서 400자로 요약한 내용",
        "keywords": ["키워드1", "키워드2"],
        "category_keywords": ["블로그", "카페"],
        "comments": ["작성자1 | 댓글내용1 | YYYY-MM-DD", "작성자2 | 댓글내용2 | YYYY-MM-DD"],
        "image_links": {{"이미지캡션1": "https://example.com/image1.jpg", "이미지캡션2": "https://example.com/image2.jpg" }},
        "links": {{"캡션1": "https://example.com/image1.jpg", "캡션2": "https://example.com/image2.jpg" }},
        "media_links": {{"캡션1": "https://example.com/image1.jpg", "캡션2": "https://example.com/image2.jpg" }},
        "file_download_links": {{"캡션1 | 10MB": "https://example.com/image1.jpg", "캡션2 | 1.1GB": "https://example.com/image2.jpg" }},
        "content_length": "MM"
    }}

    모든 응답은 유효한 JSON 형식이어야 하며, 추가적인 텍스트는 포함하지 마세요.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 정보를 추출하는 어시스턴트입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=10000
        )

        extracted_info = response['choices'][0]['message']['content'].strip()
        return extracted_info  # JSON 파싱 단계 제거

    except openai.error.AuthenticationError:
        print("오류: 인증 실패. API 키가 잘못되었거나 유효하지 않습니다.")
        return None
    except openai.error.OpenAIError as e:
        print(f"OpenAI API 오류 발생: {e}")
        return None
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        return None


load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("오류: 환경 변수 'OPENAI_API_KEY'가 설정되지 않았습니다.")


from url_to_html import url



response = requests.get(url)
print(response.status_code)  # 상태 코드를 출력


cleaned_html = clean_html_preserve_structure(response.text)
f_output = extract_information_with_gpt(cleaned_html, api_key)
#테스트용 출력
print(f_output)