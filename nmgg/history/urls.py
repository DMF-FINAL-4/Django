# history/url.py

from django.urls import path
from . import views

urlpatterns = [
    # path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('new_save/', views.new_history_save, name='new_save'),
    path('full_list/<int:list_no>', views.history_full_list, name='full_list'),
    path('id/<str:doc_id>/', views.history_id_search, name='id_search'),
    path('tag_search/', views.history_tag_search, name='tag_search'),
    path('text_search/', views.history_text_search, name='text_search'),
    path('similar_search/', views.history_similar_search, name='similar_search'),
]