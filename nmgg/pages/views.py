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
    try:
        full_list = search_full_list()
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)

    if isinstance(full_list, dict) and 'error' in full_list:
        return JsonResponse(full_list, status=400)
    return JsonResponse(full_list, safe=False)

@csrf_exempt
def id_search(request, doc_id):
    try:
        id_search_results = search_by_id(doc_id)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    if isinstance(id_search_results, dict) and 'error' in id_search_results:
        return JsonResponse(id_search_results, status=400)
    return JsonResponse(id_search_results, safe=False)

@csrf_exempt
def tag_search(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    required_fields = ['tag', 'keyword', 'method']
    missing_field_response = validate_required_fields(data, required_fields)
    if missing_field_response:
        return missing_field_response
    
    tag = data.get('tag')
    keyword = data.get('keyword')
    method = data.get('method')
    
    try:
        tag_search_results = search_by_tkm(tag, keyword, method)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    if isinstance(tag_search_results, dict) and 'error' in tag_search_results:
        return JsonResponse(tag_search_results, status=400)
    return JsonResponse(tag_search_results, safe=False)

@csrf_exempt
def text_search(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    if 'query_text' not in data:
        return JsonResponse({"error": "query_text is required"}, status=400)
    
    query_text = data.get('query_text')
    try:
        text_search_results = search_by_text(query_text)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    if isinstance(text_search_results, dict) and 'error' in text_search_results:
        return JsonResponse(text_search_results, status=400)
    return JsonResponse(text_search_results, safe=False)

@csrf_exempt
def similar_search(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    if 'doc_id' not in data:
        return JsonResponse({"error": "doc_id is required"}, status=400)
    
    doc_id = data.get('doc_id')
    try:
        similar_search_results = search_by_similarity(doc_id)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(similar_search_results, safe=False)

@csrf_exempt
def gpt_search(request):
    pass
