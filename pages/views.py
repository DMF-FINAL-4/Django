from django.shortcuts import render, redirect
from django.conf import settings # import openai_api_key, es
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json

import .utils

def new_save(response):
	is_duplycate = classify_response(response)
    if is_duplycate:
        return is_duplycate['res본문']
    raw_html = response['html']
    html_summariz = HTMLSummariz()
    summariz_json = html_summariz.presses(raw_html)
    es_res_dict = upload_to_elasticsearch(summariz_json)
    return es_res_dict

def full_list(response):
    full_list = search_full_list()
    return full_list
def search(response):
    pass

def tag_search(response):
    # 값 가져오기 및 검증
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
    
    tag_search_results = search_page_by_tkm(tag, keyword, method)

    return tag_search_results

def text_search(response):
    data = json.loads(request.body)
    if 'query_text' not in data:
         return JsonResponse({"error": "query_text is required"}, status=400)
    query_text = data.get('query_text')
    text_search_results = search_by_text(query_text)
    
    return text_search_results

def similar_search(response):
    data = json.loads(request.body)
    if 'doc_id' not in data:
         return JsonResponse({"error": "doc_id is required"}, status=400)
    doc_id = data.get('doc_id')
    similar_search_results = search_by_similarity('doc_id')

    return similar_search_results

def gpt_search(response):
    pass