from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
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
    
    def form_valid(self, form):
        product = form.save()
        messages.success(self.request, f'Producto {product.name} agregado correctamente')
        return redirect('DetailProduct', pk=product.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el producto')
        return super().form_invalid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product-update.html'
    
    def form_valid(self, form):
        product = form.save()
        messages.success(self.request, f'Producto {product.name} actualizado correctamente')
        return redirect('DetailProduct', pk=product.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el producto')
        return super().form_invalid(form)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product-delete.html'
    success_url = reverse_lazy('Products')
    
    def form_valid(self, form):
        product = self.get_object()
        product_name = product.name
        messages.success(self.request, f'{product_name} se ha eliminado de la lista de productos')
        return super().form_valid(form)
