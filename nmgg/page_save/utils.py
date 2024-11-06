# views의 가독성 향상과 함수 재사용을 위한 유틸 함수, 클래스 파일입니다. 

from bs4 import BeautifulSoup
import os
import argparse
import openai
import json
from dotenv import load_dotenv

class HTMLCleanerAndGPTExtractor:
    def __init__(self, openai_api_key):
        """
        초기화 메서드로, API 키를 초기화합니다.
        Args:
            openai_api_key (str): OpenAI API 키
        """
        self.api_key = openai_api_key
        openai.api_key = self.api_key

    def clean_html_style_tags(self, raw_html_content):
        """
        HTML 콘텐츠를 정제하여 스타일 및 장식적인 태그와 관련 속성만 제거하고 구조적인 태그는 그대로 유지합니다.
        Args:
            raw_html_content (str): 정제할 HTML 콘텐츠
        Returns:
            str: 정제된 HTML 콘텐츠
        """
        # BeautifulSoup 객체 생성 (lxml 파서 사용)
        soup = BeautifulSoup(raw_html_content, 'lxml')
        # 제거할 태그 리스트 (스타일 및 장식적인 태그)
        tags_to_remove = ['style', 'script', 'aside', 'nav', 'footer', 'header', 'iframe', 'noscript', 'form']
        # 태그와 그 내용을 완전히 제거
        for tag in tags_to_remove:
            for element in soup.find_all(tag):
                element.decompose()
        # 제거할 속성 리스트 (스타일 관련 속성)
        attributes_to_remove = ['style', 'class', 'id']
        # 모든 태그 순회
        for tag in soup.find_all(True):
            for attr in attributes_to_remove:
                if attr in tag.attrs:
                    del tag.attrs[attr]
        # 정제된 HTML 문자열 반환
        cleaned_html = str(soup)
        return cleaned_html

    def extract_information_with_gpt(self, cleaned_html):
        """
        정제된 HTML을 받아서 특정 정보를 GPT-4 모델로 요약 정리합니다.
        Args:
            cleaned_html (str): 정제된 HTML 콘텐츠
        Returns:
            dict: GPT가 추출한 정보
        """
        # 프롬프트 정의
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
            return json.loads(extracted_info)

        except openai.error.AuthenticationError:
            raise ValueError("인증 실패: API 키가 잘못되었거나 유효하지 않습니다.")
        except openai.error.OpenAIError as e:
            raise RuntimeError(f"OpenAI API 오류 발생: {e}")
        except json.JSONDecodeError:
            raise ValueError("GPT 응답을 JSON으로 변환하는 중 오류 발생.")
        except Exception as e:
            raise RuntimeError(f"예상치 못한 오류 발생: {e}")

    def process_url(self, url):
        """
        URL을 받아 HTML을 클리닝하고 GPT 모델로 정보를 추출합니다.
        Args:
            url (str): 처리할 웹 페이지의 URL
        Returns:
            dict: 추출된 정보
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            raw_html = response.text
            cleaned_html = self.clean_html_style_tags(raw_html)
            extracted_info = self.extract_information_with_gpt(cleaned_html)
            return extracted_info
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"요청 실패: {e}")

    def process_raw_html(self, raw_html):
        """
        정제되지 않은 HTML을 받아 클리닝하고 GPT 모델로 정보를 추출합니다.
        Args:
            raw_html (str): 처리할 HTML 콘텐츠
        Returns:
            dict: 추출된 정보
        """
        cleaned_html = self.clean_html_style_tags(raw_html)
        extracted_info = self.extract_information_with_gpt(cleaned_html)
        return extracted_info