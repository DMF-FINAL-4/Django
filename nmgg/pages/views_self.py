# views.py
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json

from .utils import *

@csrf_exempt
def new_save(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    try:
        classification = classify_response(data)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    if classification:
        # 중복이 있는 경우, 중복된 문서 리스트 반환
        return JsonResponse({
            "error": "Duplicate content found",
            "duplicates": classification
        }, status=400)
    
    # 중복이 없는 경우 진행
    raw_html = data.get('html')
    if not raw_html:
        return JsonResponse({"error": "HTML content is required"}, status=400)
    
    html_summarizer = HTMLSummariz()
    summariz_json = html_summarizer.process(raw_html)
    
    if 'error' in summariz_json:
        return JsonResponse(summariz_json, status=500)
    
    try:
        es_res_dict = upload_to_elasticsearch(summariz_json)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(es_res_dict, status=201)

@csrf_exempt
def full_list(request):
    full_list = search_full_list()

    if isinstance(full_list, dict) and 'error' in full_list:
        return JsonResponse(full_list, status=400)
    return JsonResponse(full_list, safe=False)


@csrf_exempt
def id_search(request, doc_id):
    id_search_results = search_by_id(doc_id)
    
    if isinstance(full_list, dict) and 'error' in full_list:
        return JsonResponse(full_list, status=400)
    return JsonResponse(id_search_results, safe=False)



@csrf_exempt
def tag_search(request):
    data = json.loads(request.body)
    required_fields = ['tag', 'keyword', 'method']
    for field in required_fields:
        if field not in data:
            return JsonResponse({"error": f"{field} is required"}, status=400)
    
    tag = data.get('tag')
    keyword = data.get('keyword')
    method = data.get('method')
    tag_search_results = search_by_tkm(tag, keyword, method)
    
    if isinstance(tag_search_results, dict) and 'error' in tag_search_results:
        return JsonResponse(tag_search_results, status=400)
    return JsonResponse(tag_search_results, safe=False)


@csrf_exempt
def text_search(request):
    data = json.loads(request.body)
    if 'query_text' not in data:
         return JsonResponse({"error": "query_text is required"}, status=400)
    query_text = data.get('query_text')
    text_search_results = search_by_text(query_text)
    
    if isinstance(text_search_results, dict) and 'error' in text_search_results:
        return JsonResponse(text_search_results, status=400)
    return JsonResponse(text_search_results, safe=False)

@csrf_exempt
def similar_search(request):
    data = json.loads(request.body)
    if 'doc_id' not in data:
         return JsonResponse({"error": "doc_id is required"}, status=400)
    doc_id = data.get('doc_id')
    similar_search_results = search_by_similarity(doc_id)
    
    if isinstance(similar_search_results, dict) and 'error' in similar_search_results:
        return JsonResponse(similar_search_results, status=400)
    return similar_search_results

@csrf_exempt
def gpt_search(request):
    pass