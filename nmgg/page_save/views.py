from django.shortcuts import render

from django.conf import settings

# Create your views here.
from .utils import HTML_cleaner_and_GPT_extractor


def get api keys

@csrf_exempt
def process_new_page(request):
    if request.method == 'POST':
        raw_html = request.body