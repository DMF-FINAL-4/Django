from django.urls import path
from . import views

urlpatterns = [
    # path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('new_save/', views.new_save, name='new_save'),
    path('full_list/', views.full_list, name='full_list'),
     path('id/<int:doc_id>/', views.id_search, name='id_search'),
    path('tag_search/', views.tag_search, name='tag_search'),
    path('text_search/', views.text_search, name='text_search'),
    path('similar_search/', views.similar_search, name='similar_search'),
    # path('gpt_search/', views.gpt_search, name='gpt_search'),
]