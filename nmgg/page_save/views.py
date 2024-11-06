from django.shortcuts import render

# Create your views here.
from .utils import HTML_cleaner_and_GPT_extractor


import os
import json
from dotenv import load_dotenv

def new_page(requests):
    # API 키 로드
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("오류: 환경 변수 'OPENAI_API_KEY'가 설정되지 않았습니다.")
    else:
        # HTML_cleaner_and_GPT_extractor 인스턴스 생성
        extractor = HTML_cleaner_and_GPT_extractor(api_key)
        # 또는 원시 HTML을 처리하고 싶을 때 사용
        raw_html = requests.body()
        try:
            extracted_info = extractor.process_raw_html(raw_html)
            if extracted_info:
                return extracted_info
                # 추출된 정보 출력
                # print(json.dumps(extracted_info, ensure_ascii=False, indent=4))
        except Exception as e:
            print(f"오류 발생: {e}")