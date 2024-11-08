# from django.shortcuts import render

from django.conf import settings # import openai_api_key, es

from .utils import HTMLCleanerAndGPTExtractor

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from elasticsearch import Elasticsearch, TransportError, ConnectionError, NotFoundError

@csrf_exempt
def process_new_page(request):
    if request.method == 'POST':
        try:
            # HTML 프로세스
            print("HTML 프로세스 시도")
            raw_html = request.body.decode('utf-8')

            # API 키 등록 확인
            print("API 키 가져오기 시도")
            openai_api_key = settings.OPENAI_API_KEY
            if not openai_api_key:
                print("API 키가 설정되지 않았음")
                return JsonResponse({'error': 'API key not found'}, status=500)

            # HTMLCleanerAndGPTExtractor 클래스 인스턴스화
            print("HTMLCleanerAndGPTExtractor 인스턴스화 시도")
            processer = HTMLCleanerAndGPTExtractor(openai_api_key)

            try:
                processed_data = processer.process_raw_html(raw_html)
                print("HTML 프로세스 성공:", processed_data)
            except Exception as e:
                # HTML 처리 중 오류 발생 시 처리
                print(f"HTML 처리 중 오류 발생: {str(e)}")
                return JsonResponse({'status': 'error', 'message': 'Failed to process HTML'}, status=400)


            # Elasticsearch 클라이언트 초기화
            print("Elasticsearch 클라이언트 초기화 시도")
            es = settings.ELASTICSEARCH
            if not es:
                print("Elasticsearch 클라이언트가 설정되지 않음")
                return JsonResponse({'error': 'Elasticsearch client not configured'}, status=500)

            # Elasticsearch에 데이터 업로드 시도
            print("Elasticsearch에 데이터 업로드 시도")
            try:
                res = es.index(index='pages', body=processed_data)

                # 응답을 딕셔너리 형식으로 변환
                if hasattr(res, 'to_dict'):
                    res_dict = res.to_dict()  # to_dict() 메서드를 사용하여 변환
                else:
                    res_dict = dict(res)  # 이미 딕셔너리인 경우 그대로 사용

                print("Elasticsearch 업로드 성공:", res_dict)
                return JsonResponse({'status': 'success', 'data': res_dict}, status=200)
            except Exception as e:
                print("Elasticsearch 업로드 중 알 수 없는 오류 발생:", str(e))
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        except Exception as e:
            # 다른 모든 예외 처리
            print(f"처리 중 오류 발생: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # 잘못된 메서드의 경우
    else:
        print("POST 이외의 요청 수신")
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)




from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse
import requests
from .utils import HTMLCleanerAndGPTExtractor
import json

@csrf_exempt
def process_new_urls(request):
    if request.method == 'POST':
        es = settings.ELASTICSEARCH
        # API 키 등록
        openai_api_key = settings.OPENAI_API_KEY
        if not openai_api_key:
            return JsonResponse({'error': 'API key not found'}, status=500)

        # URL 가져오기
        try:
            body = json.loads(request.body)
            url = body.get('url')
            if not url:
                return JsonResponse({'status': 'error', 'message': 'No URL provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

        # HTML 콘텐츠 가져오기
        try:
            response = requests.get(url)
            response.raise_for_status()  # 요청에 오류가 있을 경우 예외 발생
            raw_html = response.text
        except requests.exceptions.RequestException as e:
            return JsonResponse({'status': 'error', 'message': f'Failed to retrieve HTML from URL: {str(e)}'}, status=400)

        # 클래스 인스턴스화 및 HTML 정제 및 데이터 추출
        processer = HTMLCleanerAndGPTExtractor(openai_api_key)
        try:
            processed_data = processer.process_raw_html(raw_html)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        # Elasticsearch에 데이터 업로드
        try:
            res = es.index(index='pages', body=processed_data)
            # 성공 시 응답 반환
            print("Elasticsearch 업로드 성공:", res)
            return JsonResponse({'status': 'success', 'data': res}, status=200)
        except Exception as e:
            print("Elasticsearch 업로드 중 알 수 없는 오류 발생:", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    # 잘못된 메서드의 경우
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
