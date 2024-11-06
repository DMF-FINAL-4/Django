# from django.shortcuts import render

from django.conf import settings # import openai_api_key

from .utils import HTMLCleanerAndGPTExtractor


@csrf_exempt
def process_new_page(request):
    if request.method == 'POST':
        raw_html = request.body