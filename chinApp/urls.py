from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.translation_view, name='translation_view'),
]