# views.py
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json

from .utils import *

def new_save(request):
    is_duplicate = classify_request(request)
    if is_duplicate == False:
        return is_duplicate['res본문']
    raw_html = response['html']

    html_summariz = HTMLSummariz()
    summariz_json = html_summariz.presses(raw_html)
    es_res_dict = upload_to_elasticsearch(summariz_json)
    return es_res_dict

def full_list(request):
    full_list = search_full_list()

    return full_list


def id_search(request, doc_id):
    
    # data = json.loads(request.body)
    # if 'doc_id' not in data:
    #      return JsonResponse({"error": "doc_id is required"}, status=400)
    # doc_id = data.get('doc_id')
    id_search_results = search_by_id(doc_id)

    return id_search_results

def tag_search(request):
    data = json.loads(request.body)
    if 'tag' not in data:
        return JsonResponse({"error": "Tag is required"}, status=400)
    if 'keyword' not in data:
        return JsonResponse({"error": "keyword is required"}, status=400)
    if 'method' not in data:
        return JsonResponse({"error": "method is required"}, status=400)

    tag = data.get('tag')
    keyword = data.get('keyword')
    method = data.get('method')
    tag_search_results = search_by_tkm(tag, keyword, method)

    return tag_search_results

def text_search(request):
    data = json.loads(request.body)
    if 'query_text' not in data:
         return JsonResponse({"error": "query_text is required"}, status=400)
    query_text = data.get('query_text')
    text_search_results = search_by_text(query_text)
    
    return text_search_results

def similar_search(request):
    data = json.loads(request.body)
    if 'doc_id' not in data:
         return JsonResponse({"error": "doc_id is required"}, status=400)
    doc_id = data.get('doc_id')
    similar_search_results = search_by_similarity('doc_id')

    return similar_search_results

def gpt_search(request):
    pass