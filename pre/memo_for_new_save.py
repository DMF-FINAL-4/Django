from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from elasticsearch import Elasticsearch

# CSRF 검증을 비활성화 (API 엔드포인트인 경우)
@csrf_exempt
def process_new_page(request):
    if request.method == 'POST':
        try:
            # 요청 본문에서 JSON 데이터 가져오기
            data = json.loads(request.body)
            
            # 데이터 전처리 (여기에 필요한 전처리 로직 추가)
            processed_data = preprocess_data(data)
            
            # Elasticsearch 클라이언트 설정
            es = Elasticsearch(['http://localhost:9200'])  # Elasticsearch 서버 주소
            
            # Elasticsearch에 데이터 업로드
            res = es.index(index='pages', body=processed_data)
            
            return JsonResponse({'status': 'success', 'data': res}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def preprocess_data(data):
    # 여기서 데이터 전처리 로직을 구현
    # 예: 특정 필드 정리, 데이터 형 변환 등
    return data  # 전처리된 데이터 반환



    
import os
from dotenv import load_dotenv

def new_page(requests):
    # API 키 로드
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from elasticsearch import Elasticsearch
import json

@csrf_exempt
def page_save(request):
    if request.method == 'POST':
        try:
            # 요청에서 문자열 데이터를 가져옴
            raw_text = request.body.decode('utf-8')

            # Elasticsearch 클라이언트 설정
            es = Elasticsearch(['http://localhost:9200'])  # Elasticsearch 서버 주소
            
            # Elasticsearch에 데이터 업로드
            # 데이터는 index라는 메서드를 통해 업로드됩니다.
            res = es.index(index='pages', body={'content': raw_text})

            # 성공적으로 업로드되면 응답 반환
            return JsonResponse({'status': 'success', 'data': res}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)




        // 예시: JavaScript를 사용한 POST 요청
fetch('/pagesave/', {
    method: 'POST',
    headers: {
        'Content-Type': 'text/plain',
    },
    body: "여기에 전송할 문자열 데이터를 입력하세요.",
})
.then(response => response.json())
.then(data => {
    if (data.status === 'success') {
        console.log('데이터 업로드 성공:', data);
    } else {
        console.error('에러 발생:', data.message);
    }
})
.catch((error) => {
    console.error('요청 실패:', error);
});
