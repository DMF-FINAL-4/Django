#GPTsearch/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('gpt_search/', views.gpt_search, name='gpt_search'),
]
