# from django.shortcuts import render

from django.conf import settings # import openai_api_key, es

from .utils import HTMLCleanerAndGPTExtractor

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


import logging
# Django의 기본 로깅 시스템을 사용하거나 새 로그 객체를 생성합니다.
logger = logging.getLogger('Django')


#로그 없는 함수
# @csrf_exempt
# def process_new_page(request):
#     if request.method == 'POST':
#         try:
#             # Elasticsearch 클라이언트 초기화
#             es = settings.ELASTICSEARCH
#             if not es:
#                 return JsonResponse({'error': 'Elasticsearch client not configured'}, status=500)

#             # API 키 등록
#             openai_api_key = settings.OPENAI_API_KEY
#             if not openai_api_key:
#                 return JsonResponse({'error': 'API key not found'}, status=500)

#             # 클래스 인스턴스화
#             processer = HTMLCleanerAndGPTExtractor(openai_api_key)

#             # HTML 프로세스
#             # request.body는 바이트 데이터이므로 문자열로 디코딩
#             raw_html = request.body.decode('utf-8')
#             processed_data = processer.process_raw_html(raw_html)

#             # Elasticsearch에 데이터 업로드
#             try:
#                 res = es.index(index='pages', body=processed_data)
#                 # 성공적으로 업로드되면 응답 반환
#                 return JsonResponse({'status': 'success', 'data': res}, status=200)
#             except Exception as e:
#                 return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

#         except Exception as e:
#             # 다른 모든 예외 처리
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

#     # 잘못된 메서드의 경우
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


    



#로그 있는 함수
@csrf_exempt
def process_new_page(request):
    logger.info("process_new_page 함수 호출됨")
    
    if request.method == 'POST':
        try:
            # Elasticsearch 클라이언트 초기화
            logger.info("Elasticsearch 클라이언트 초기화 시도")
            es = settings.ELASTICSEARCH
            if not es:
                logger.error("Elasticsearch 클라이언트가 설정되지 않음")
                return JsonResponse({'error': 'Elasticsearch client not configured'}, status=500)

            # API 키 등록 확인
            logger.info("API 키 가져오기 시도")
            openai_api_key = settings.OPENAI_API_KEY
            if not openai_api_key:
                logger.error("API 키가 설정되지 않았음")
                return JsonResponse({'error': 'API key not found'}, status=500)

            # HTMLCleanerAndGPTExtractor 클래스 인스턴스화
            logger.info("HTMLCleanerAndGPTExtractor 인스턴스화 시도")
            processer = HTMLCleanerAndGPTExtractor(openai_api_key)

            # HTML 프로세스
            logger.info("HTML 프로세스 시도")
            raw_html = request.body.decode('utf-8')  # request.body를 문자열로 디코딩
            processed_data = processer.process_raw_html(raw_html)
            logger.info("HTML 프로세스 성공")

            # Elasticsearch에 데이터 업로드
            logger.info("Elasticsearch에 데이터 업로드 시도")
            try:
                res = es.index(index='pages', body=processed_data)
                logger.info(f"Elasticsearch 업로드 성공: {res}")
                return JsonResponse({'status': 'success', 'data': res}, status=200)
            except Exception as e:
                logger.error(f"Elasticsearch 업로드 오류: {str(e)}")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        except Exception as e:
            # 다른 모든 예외 처리
            logger.error(f"처리 중 오류 발생: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # 잘못된 메서드의 경우
    else:
        logger.warning("POST 이외의 요청 수신")
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
