# history/views.py

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

import json
from .utils import *

@require_http_methods(["POST"])
@csrf_exempt
def new_history_save(request):
    try:
        data = json.loads(request.body)
        print('1')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    print('2')
    url = data.get('url')
    html = data.get('html')
    
    if not url or not html:
        return JsonResponse({"error": "URL and HTML content are required"}, status=400)
    print('3')
    try:
        print('3.1')
        favicon, title, cleaned_content = process_html(html, url)
        print('3.2')
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    print(favicon, title, cleaned_content)
    print('4')
    processed_data = {
        "url": url,
        "favicon": favicon,
        "title": title,
        "content": cleaned_content
    }
    print('5')
    try:
        es_res_dict = upload_to_elasticsearch_history(processed_data)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    print('6!')
    return JsonResponse(es_res_dict, status=201)

@require_http_methods(["GET"])
@csrf_exempt
def history_full_list(request):
    try:
        full_list = search_full_list_history()
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(full_list, safe=False)

@require_http_methods(["GET"])
@csrf_exempt
def history_id_search(request, doc_id):
    try:
        id_search_results = search_by_id_history(doc_id)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(id_search_results, safe=False)

@require_http_methods(["GET"])
@csrf_exempt
def history_text_search(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    if 'query_text' not in data:
        return JsonResponse({"error": "query_text is required"}, status=400)
    
    query_text = data.get('query_text')
    try:
        text_search_results = search_by_text_history(query_text)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(text_search_results, safe=False)

@require_http_methods(["GET"])
@csrf_exempt
def history_tag_search(request):
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
        tag_search_results = search_by_tkm_history(tag, keyword, method)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(tag_search_results, safe=False)

@require_http_methods(["GET"])
@csrf_exempt
def history_similar_search(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    if 'doc_id' not in data:
        return JsonResponse({"error": "doc_id is required"}, status=400)
    
    doc_id = data.get('doc_id')
    try:
        similar_search_results = search_by_similarity_history(doc_id)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(similar_search_results, safe=False)
