from django.urls import path
from . import views

urlpatterns = [
    # path('', views.full_list, name='full_list'),
    # path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('new_page/', views.process_new_page, name='new_page'),
    path('new_url/', views.process_new_url, name='new_url'),
    path('search/', views.process_search, name='search'),
]