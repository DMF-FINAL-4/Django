from django.shortcuts import render

# Create your views here.
# views.py for blackbox app
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json
from .utils import *

@csrf_exempt
def new_blackbox_save(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    url = data.get('url')
    html = data.get('html')

    if not url or not html:
        return JsonResponse({"error": "URL and HTML content are required"}, status=400)

    try:
        favicon, title, cleaned_content = process_html(html, url)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    processed_data = {
        "url": url,
        "favicon": favicon,
        "title": title,
        "content": cleaned_content
    }

    try:
        es_res_dict = upload_to_elasticsearch_blackbox(processed_data)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(es_res_dict, status=201)

@csrf_exempt
def blackbox_full_list(request):
    try:
        full_list = search_full_list_blackbox()
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(full_list, safe=False)

@csrf_exempt
def blackbox_id_search(request, doc_id):
    try:
        id_search_results = search_by_id_blackbox(doc_id)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(id_search_results, safe=False)