from django.urls import path
from main.views import index, about, search

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='About'),
    path('search/', search, name='Search'),
    #path('filter_search/', filter_search, name='FilterSearch'),
]