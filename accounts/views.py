from django.shortcuts import render
from django.http import HttpResponse
from accounts.models import *
from accounts.forms import *
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


@login_required
def accounts_view(request):
    return render(request, 'accounts/accounts.html')

#-------[ VISTAS CLIENTES ]-------
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    context_object_name = 'clients'
    template_name = 'accounts/client-list.html'

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    context_object_name = 'client'
    template_name = 'accounts/client-detail.html'

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'accounts/client-create.html'
    success_url = reverse_lazy('Clients')

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = 'accounts/client-update.html'
    form_class = ClientForm
    success_url = reverse_lazy('Clients')

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'accounts/client-delete.html'
    success_url = reverse_lazy('Clients')



#-------[ VISTAS PROVEEDORES ]-------
class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    context_object_name = 'suppliers'
    template_name = 'accounts/supplier-list.html'

class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    context_object_name = 'supplier'
    template_name = 'accounts/supplier-detail.html'

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'accounts/supplier-create.html'
    success_url = reverse_lazy('Suppliers')

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'accounts/supplier-update.html'
    success_url = reverse_lazy('Suppliers')

class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'accounts/supplier-delete.html'
    success_url = reverse_lazy('Suppliers')

