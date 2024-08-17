from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product
from products.forms import ProductForm

# Create your views here.
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'products/products.html'

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'products/product-detail.html'

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product-create.html'
    success_url = reverse_lazy('Products')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product-update.html'
    success_url = reverse_lazy('Products')

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product-delete.html'
    success_url = reverse_lazy('Products')
