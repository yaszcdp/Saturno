from django.urls import path
from products.views import *

urlpatterns = [
    path('', ProductListView.as_view(), name='Products'),
    path('create/', ProductCreateView.as_view(), name='CreateProduct'),
    path('detail/<int:pk>/', ProductDetailView.as_view(), name='DetailProduct'),
    path('update/<int:pk>/', ProductUpdateView.as_view(), name='UpdateProduct'),
    path('delete/<int:pk>/', ProductDeleteView.as_view(), name='DeleteProduct'),
]