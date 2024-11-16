# pages/url.py

from django.urls import path
from . import views

urlpatterns = [
    path('new_save/', views.new_save, name='new_save'),
    path('full_list/<int:list_no>', views.full_list, name='full_list'),
    path('id/<str:doc_id>/', views.id_search, name='id_search'),
    path('tag_search/', views.tag_search, name='tag_search'),
    path('text_search/', views.text_search, name='text_search'),
    path('similar_search/', views.similar_search, name='similar_search'),
]