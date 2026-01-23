from django.shortcuts import render, redirect
from django.http import HttpResponse
from accounts.models import *
from accounts.forms import *
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def accounts_view(request):
    return render(request, 'accounts/accounts.html')

#-------[ VISTAS CLIENTES ]-------
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    context_object_name = 'clients'
    template_name = 'accounts/account-list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = Client.objects.all().order_by('first_name')
        query = self.request.GET.get('search_query', '')
        if query:
            qs = qs.filter(first_name__icontains=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'Clientes'
        params = self.request.GET.copy()
        if params.get('page'):
            del params['page']
            context['params'] = params.urlencode()
        return context


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    context_object_name = 'client'
    template_name = 'accounts/client-detail.html'

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'accounts/account-create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'Cliente'
        return context
    
    def form_valid(self, form):
        client = form.save()
        messages.success(self.request, f'Cliente {client.first_name} {client.last_name} agregado correctamente')
        return redirect('DetailClient', pk=client.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el cliente')
        return super().form_invalid(form)

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = 'accounts/client-update.html'
    form_class = ClientForm
    
    def form_valid(self, form):
        client = form.save()
        messages.success(self.request, f'Cliente {client.first_name} {client.last_name} actualizado correctamente')
        return redirect('DetailClient', pk=client.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el cliente')
        return super().form_invalid(form)

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'accounts/client-delete.html'
    success_url = reverse_lazy('Clients')
    
    def form_valid(self, form):
        client = self.get_object()
        client_name = f'{client.first_name} {client.last_name}'
        messages.success(self.request, f'{client_name} se ha eliminado de la lista de clientes')
        return super().form_valid(form)



#-------[ VISTAS PROVEEDORES ]-------
class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    context_object_name = 'suppliers'
    template_name = 'accounts/account-list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = Supplier.objects.all().order_by('company')
        query = self.request.GET.get('search_query', '')
        if query:
            qs = qs.filter(company__icontains=query)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'Proveedores'
        params = self.request.GET.copy()
        if params.get('page'):
            del params['page']
            context['params'] = params.urlencode()
        return context

class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    context_object_name = 'supplier'
    template_name = 'accounts/supplier-detail.html'

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'accounts/account-create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'Proveedor'
        return context
    
    def form_valid(self, form):
        supplier = form.save()
        messages.success(self.request, f'Proveedor {supplier.company} agregado correctamente')
        return redirect('DetailSupplier', pk=supplier.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el proveedor')
        return super().form_invalid(form)

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'accounts/supplier-update.html'
    
    def form_valid(self, form):
        supplier = form.save()
        messages.success(self.request, f'Proveedor {supplier.company} actualizado correctamente')
        return redirect('DetailSupplier', pk=supplier.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el proveedor')
        return super().form_invalid(form)

class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'accounts/supplier-delete.html'
    success_url = reverse_lazy('Suppliers')
    
    def form_valid(self, form):
        supplier = self.get_object()
        supplier_name = supplier.company
        messages.success(self.request, f'{supplier_name} se ha eliminado de la lista de proveedores')
        return super().form_valid(form)

