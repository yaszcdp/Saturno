from django.urls import path
from main.views import index, about

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='About'),
]