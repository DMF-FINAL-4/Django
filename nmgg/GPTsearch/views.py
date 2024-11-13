# GPTsearch/views.py

from django.conf import settings
from django.http import JsonResponse
from .utils import analyze_user_question, execute_es_query, analyze_es_results
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import json

@require_http_methods(["GET"])
@csrf_exempt
def gpt_search(request):
    if request.method == 'POST':
        try:
            # 요청에서 데이터 추출
            data = json.loads(request.body)
            user_question = data.get('question')
            index_type = data.get('index')

            # 인덱스 선택에 따른 분기 처리
            if index_type == 'post':
                index_name = 'posts'
            elif index_type == 'history':
                index_name = 'history'
            else:
                return JsonResponse({'error': 'Invalid index type provided.'}, status=400)

            # Step 1: Use GPT to analyze the question and generate the appropriate ES query
            analysis = analyze_user_question(user_question, index_name)

            if "error" in analysis:
                return JsonResponse(analysis, status=500)

            # Step 2: Execute the Elasticsearch query
            query = analysis.get("query")
            query_results = execute_es_query(query, index_name)

            if "error" in query_results:
                return JsonResponse(query_results, status=500)

            # Step 3: Process the Elasticsearch results based on question type
            if analysis.get("question_type") == "list":
                return JsonResponse({"results": query_results}, status=200)
            elif analysis.get("question_type") == "info":
                # Analyze results and get the most relevant document ID
                relevant_doc_id = analyze_es_results(query_results, user_question)
                return JsonResponse({"relevant_document_id": relevant_doc_id}, status=200)

        except Exception as e:
            return JsonResponse({'error': f'Error processing request: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
