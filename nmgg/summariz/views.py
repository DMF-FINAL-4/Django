# from django.shortcuts import render

from django.conf import settings # import openai_api_key, es

from .utils import HTMLCleanerAndGPTExtractor, es_upload_to_pages

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from elasticsearch import Elasticsearch, TransportError, ConnectionError, NotFoundError

@csrf_exempt
def process_new_page(request):
    if request.method == 'POST':

        # HTML 프로세스
        print("HTML 받아오기 시도")
        try:
            json_body = json.loads(request.body.decode('utf-8'))
            raw_html = json_body.get('html')
            if not raw_html:
                return JsonResponse({'status': 'error', 'message': 'No HTML provided'}, status=400)
        
            # HTMLCleanerAndGPTExtractor 클래스 인스턴스화
            print("HTMLCleanerAndGPTExtractor 인스턴스화 시도")
            processer = HTMLCleanerAndGPTExtractor()

            # HTML 프로세스 처리
            processed_data = processer.process_raw_html(raw_html)
            if processed_data('error'):
                return {"error": "알 수 없는 오류 발생", "details": processed_data('details')}
            print("url 프로세스 성공")

            # Elasticsearch에 데이터 업로드 시도
            res_dict = es_upload_to_pages(processed_data)
            print("Elasticsearch에 데이터 업로드 성공")

            # 성공적으로 처리된 경우 응답 반환
            return JsonResponse({'status': 'success', 'data': res_dict}, status=200)

        except json.JSONDecodeError:
            print("HTML 불러오기 오류")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except ValueError as ve:
            print(f"ValueError 발생: {str(ve)}")
            return JsonResponse({'status': 'error', 'message': str(ve)}, status=400)
        except RuntimeError as re:
            print(f"RuntimeError 발생: {str(re)}")
            return JsonResponse({'status': 'error', 'message': str(re)}, status=500)
        except Exception as e:
            # 기타 모든 예외 처리
            print(f"처리 중 알 수 없는 오류 발생: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'An unknown error occurred'}, status=500)

    # 잘못된 메서드의 경우
    else:
        print("POST 이외의 요청 수신")
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



@csrf_exempt
def process_new_url(request):
    if request.method == 'POST':

        # URL 가져오기
        try:
            body = json.loads(request.body)
            url = body.get('url')
            if not url:
                return JsonResponse({'status': 'error', 'message': 'No URL provided'}, status=400)

            # HTMLCleanerAndGPTExtractor 클래스 인스턴스화
            print("HTMLCleanerAndGPTExtractor 인스턴스화 시도")
            processer = HTMLCleanerAndGPTExtractor()

            # HTML 프로세스 처리
            processed_data = processer.process_url(url)
            if processed_data('error'):
                return {"error": "알 수 없는 오류 발생", "details": processed_data('details')}
            print("url 프로세스 성공")

            # Elasticsearch에 데이터 업로드 시도
            res_dict = es_upload_to_pages(processed_data)
            print("Elasticsearch에 데이터 업로드 성공")

            # 성공적으로 처리된 경우 응답 반환
            return JsonResponse({'status': 'success', 'data': res_dict}, status=200)

        except json.JSONDecodeError:
            print("HTML 불러오기 오류")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except ValueError as ve:
            print(f"ValueError 발생: {str(ve)}")
            return JsonResponse({'status': 'error', 'message': str(ve)}, status=400)
        except RuntimeError as re:
            print(f"RuntimeError 발생: {str(re)}")
            return JsonResponse({'status': 'error', 'message': str(re)}, status=500)
        except Exception as e:
            # 기타 모든 예외 처리
            print(f"처리 중 알 수 없는 오류 발생: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'An unknown error occurred'}, status=500)

    # 잘못된 메서드의 경우
    else:
        print("POST 이외의 요청 수신")
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)




@csrf_exempt
def process_search(request):
    if request.method == 'POST':
        try:
            # 요청에서 검색어를 가져옴
            request_data = json.loads(request.body)
            query = request_data.get('query', '')

            print('검색어 가져옴')

            if not query:
                return JsonResponse({'error': '검색어가 제공되지 않았습니다.'}, status=400)

            # 검색 쿼리 구성
            body = {
                "query": {
                    "match": {
                        "content": query
                    }
                }
            }

            es = settings.ELASTICSEARCH
            print('검색 요청 시작')
            # Elasticsearch에 검색 요청
            res = es.search(index="pages", body=body)
            hits = res.get('hits', {}).get('hits', [])
            
            print('결과 정제 시작')
            # 검색 결과 정제
            results = []
            for hit in hits:
                source = hit.get('_source', {})
                results.append({
                    "title": source.get("title"),
                    "author": source.get("author"),
                    "date": source.get("date"),
                    # "content": source.get("content"),
                    "url": source.get("alternate_url")
                })
            
            print(results)

            return JsonResponse({"results": results}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON 형식이 잘못되었습니다.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)