from django.urls import path
from . import views

urlpatterns = [
    path('search-form/', views.search_form, name='search_form'),
    path('search/', views.search, name='search'),
    
]
