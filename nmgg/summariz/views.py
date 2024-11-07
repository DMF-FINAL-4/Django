# from django.shortcuts import render

from django.conf import settings # import openai_api_key, es

from .utils import HTMLCleanerAndGPTExtractor

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


@csrf_exempt
def process_new_page(request):
    if request.method == 'POST':
        try:
            # request.body 문자열로 디코딩
            raw_html = request.body.decode('utf-8')

            # API 키 등록
            openai_api_key = settings.OPENAI_API_KEY
            if not openai_api_key:
                return JsonResponse({'error': 'API key not found'}, status=500)

            # 클래스 인스턴스화
            processer = HTMLCleanerAndGPTExtractor(openai_api_key)

             # HTML 프로세스
            processed_data = processer.process_raw_html(raw_html)

            # Elasticsearch 클라이언트 초기화
            es = settings.ELASTICSEARCH
            if not es:
                return JsonResponse({'error': 'Elasticsearch client not configured'}, status=500)
            print("업로드 시작")
            # Elasticsearch에 데이터 업로드
            try:
                res = es.index(index='pages', body=processed_data)
                # 성공적으로 업로드되면 응답 반환
                print("업로드 성공")
                return JsonResponse({'status': 'success', 'data': res}, status=200)
            except Exception as e:
                print("업로드 실패")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        except Exception as e:
            # 다른 모든 예외 처리
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # POST 외의 메서드의 경우
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
