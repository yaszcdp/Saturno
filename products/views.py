from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from products.models import Product, ProductBatch
from products.forms import ProductForm, ProductBatchForm
from accounts.models import Client, Supplier
from decimal import Decimal

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

class LoadMerchandiseView(LoginRequiredMixin, View):
    """Vista para cargar mercadería (crear lotes de productos)"""
    template_name = 'products/load-merchandise.html'
    
    def get(self, request):
        batch_form = ProductBatchForm()
        product_form = ProductForm()
        
        context = {
            'batch_form': batch_form,
            'product_form': product_form,
            'suppliers': Supplier.objects.all(),
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        product_option = request.POST.get('product_option', 'existing')
        
        # Si es producto nuevo, crear primero el producto
        if product_option == 'new':
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                product = product_form.save()
            else:
                messages.error(request, 'Error al crear el producto')
                return self.render_with_forms(request, product_form=product_form)
        else:
            product_id = request.POST.get('product')
            if not product_id:
                messages.error(request, 'Debe seleccionar un producto')
                return self.render_with_forms(request)
            product = Product.objects.get(pk=product_id)
        
        # Obtener datos del proveedor
        supplier_id = request.POST.get('supplier_id')
        supplier = Supplier.objects.get(pk=supplier_id) if supplier_id else None
        
        # Calcular costo por unidad
        initial_quantity = Decimal(request.POST.get('initial_quantity', 0))
        base_price = Decimal(request.POST.get('base_price', 0))
        transport_cost = Decimal(request.POST.get('transport_cost', 0))
        entry_cost = Decimal(request.POST.get('entry_cost', 0))
        
        if initial_quantity > 0:
            cost_per_unit = (base_price + transport_cost + entry_cost) / initial_quantity
        else:
            cost_per_unit = Decimal(0)
        
        # Crear el lote
        batch = ProductBatch.objects.create(
            product=product,
            supplier=supplier,
            entry_date=request.POST.get('entry_date', timezone.now().date()),
            initial_quantity=initial_quantity,
            base_price=base_price,
            transport_cost=transport_cost,
            entry_cost=entry_cost,
            cost_per_unit=cost_per_unit,
            suggested_price=Decimal(request.POST.get('suggested_price', 0)),
            notes=request.POST.get('notes', '')
        )
        
        messages.success(request, f'Lote de {product.name} cargado correctamente')
        return redirect('Products')
    
    def render_with_forms(self, request, batch_form=None, product_form=None):
        if not batch_form:
            batch_form = ProductBatchForm()
        if not product_form:
            product_form = ProductForm()

        context = {
            'batch_form': batch_form,
            'product_form': product_form,
            'suppliers': Supplier.objects.all(),
        }
        return render(request, self.template_name, context)


@login_required
@require_POST
def create_product_ajax(request):
    name = request.POST.get('name', '').strip()
    price = request.POST.get('price', '').strip()
    unit = request.POST.get('unit', '').strip()
    category = request.POST.get('category', '').strip()

    if not name or not price:
        return JsonResponse({'error': 'Nombre y precio son obligatorios.'}, status=400)

    if Product.objects.filter(name__iexact=name).exists():
        product = Product.objects.get(name__iexact=name)
        return JsonResponse({'id': product.pk, 'name': product.name, 'price': str(product.price), 'already_exists': True})

    try:
        product = Product.objects.create(
            name=name,
            price=Decimal(price),
            unit=unit or None,
            category=category or None,
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'id': product.pk, 'name': product.name, 'price': str(product.price), 'already_exists': False})