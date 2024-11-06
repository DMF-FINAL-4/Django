# from django.shortcuts import render

from django.conf import settings # import openai_api_key, es

from .utils import HTMLCleanerAndGPTExtractor

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def process_new_page(request):
    if request.method == 'POST':

        # 클래스 인스턴스화, api 키등록
        openai_api_key = settings.OPENAI_API_KEY
        if not openai_api_key:
            return JsonResponse({'error': 'API key not found'}, status=500)
        processer = HTMLCleanerAndGPTExtractor(openai_api_key)
        # html 프로세스
        raw_html = request.body
        processed_data = processer.process_raw_html(raw_html)
        # Elasticsearch에 데이터 업로드


        # ! 이하 불필요한 요소 제거할수 있음
        # 데이터는 index라는 메서드를 통해 업로드됩니다.
        res = es.index(index='pages', body=processed_data)
        # 성공적으로 업로드되면 응답 반환
        return JsonResponse({'status': 'success', 'data': res}, status=200)
        # 오류처리
    #     except Exception as e:
    #         return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    # else:
    #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)