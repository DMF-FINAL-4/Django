from django.urls import path
from . import views

urlpatterns = [
    path('handle_user_question/', views.handle_user_question, name='handle_user_question'),
]
