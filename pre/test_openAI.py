import os
import argparse
import openai
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
from test_bs import clean_html_preserve_structure

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
    - 접근권한 : 만약 접근에 제한이 있는 페이지로 확인된다면 '에러코드', '없는 페이지', '로그인 필요' 등의 적절한 항목을 출력. 문제가 없다면 '정상'을 출력
    - 호스트 도메인 :
    - 호스트 이름 : 호스트의 이름을 한글로 출력, 한글이 없다면 영어로 출력 (예시: 네이버 뉴스, 페이스북)
    - 제목 : 각종 정보를 종합한 제목 (예시 '동아일보｜[이철희 칼럼] 형제애로 마련한 400억…감사 전한 튀르키예')
    - 본문 :
    - 요약 : 본문을 10자에서 200자로 사이로 요약
    - 작성자 :
    - 댓글 :
    - 키워드 : 본문의 키워드들
    - 유형 키워드 : 블로그, 카페, 네이버, 기사, 리뷰, 쇼핑, sns 등 사이트 유형과 관련한 키워드들
    - 작성일 : 페이지의 작성일
    - 이미지 url : 주요 이미지들의 url

    

    HTML:
    \"\"\"
    {cleaned_html}
    \"\"\"

    JSON 형식 예시:
    {{
        "host": "호스트 이름",
        "title": "제목",
        "content": "본문",
        "author": "작성자",
        "comments": ["댓글1", "댓글2", ...],
        "keywords": ["키워드1", "키워드2", ...],
        "date": "YYYY-MM-DD"
    }}
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
        json_data = json.loads(extracted_info)
        return json_data

    except json.JSONDecodeError:
        print("JSON 디코딩 오류 발생. 응답 내용:")
        print(response['choices'][0]['message']['content'])
        return None
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
extract_information_with_gpt(cleaned_html, api_key)