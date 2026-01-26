from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
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


#-------[ VISTAS GENERALIZADAS PARA PERSON ]-------
class PersonListView(LoginRequiredMixin, ListView):
    context_object_name = 'persons'
    template_name = 'accounts/account-list.html'
    paginate_by = 10

    def get_model_and_config(self):
        """Retorna el modelo y configuración según el tipo"""
        person_type = self.kwargs.get('person_type')
        
        if person_type == 'client':
            return {
                'model': Client,
                'context_name': 'clients',
                'form_type': 'Clientes',
                'search_field': 'first_name'
            }
        elif person_type == 'supplier':
            return {
                'model': Supplier,
                'context_name': 'suppliers',
                'form_type': 'Proveedores',
                'search_field': 'company'
            }
        else:
            raise Http404("Tipo de persona no válido")
    
    def get_queryset(self):
        config = self.get_model_and_config()
        model = config['model']
        search_field = config['search_field']
        
        qs = model.objects.all()
        
        # Ordenar según el tipo
        if self.kwargs.get('person_type') == 'client':
            qs = qs.order_by('first_name')
        else:
            qs = qs.order_by('company')
        
        # Filtrar por búsqueda
        query = self.request.GET.get('search_query', '')
        if query:
            filter_kwargs = {f'{search_field}__icontains': query}
            qs = qs.filter(**filter_kwargs)
        
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = self.get_model_and_config()
        
        context['person_type'] = self.kwargs.get('person_type')
        context[config['context_name']] = context['persons']
        context['form_type'] = config['form_type']
        
        params = self.request.GET.copy()
        if params.get('page'):
            del params['page']
            context['params'] = params.urlencode()
        
        return context


class PersonDetailView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/account-detail.html'
    
    def get_model_and_config(self):
        """Retorna el modelo y configuración según el tipo"""
        person_type = self.kwargs.get('person_type')
        
        if person_type == 'client':
            return {
                'model': Client,
                'context_name': 'client',
            }
        elif person_type == 'supplier':
            return {
                'model': Supplier,
                'context_name': 'supplier',
            }
        else:
            raise Http404("Tipo de persona no válido")
    
    def get_queryset(self):
        config = self.get_model_and_config()
        return config['model'].objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = self.get_model_and_config()
        
        context['person_type'] = self.kwargs.get('person_type')
        context[config['context_name']] = self.object
        
        # Agregar form_type para el título
        if self.kwargs.get('person_type') == 'client':
            context['form_type'] = 'Cliente'
        else:
            context['form_type'] = 'Proveedor'
        
        return context


class PersonCreateView(LoginRequiredMixin, CreateView):
    template_name = 'accounts/account-create.html'
    
    def get_model_and_config(self):
        """Retorna el modelo, form y configuración según el tipo"""
        person_type = self.kwargs.get('person_type')
        
        if person_type == 'client':
            return {
                'model': Client,
                'form_class': ClientForm,
                'form_type': 'Cliente',
                'detail_url': 'DetailPerson',
                'name_field': lambda obj: f'{obj.first_name} {obj.last_name}'
            }
        elif person_type == 'supplier':
            return {
                'model': Supplier,
                'form_class': SupplierForm,
                'form_type': 'Proveedor',
                'detail_url': 'DetailPerson',
                'name_field': lambda obj: obj.company
            }
        else:
            raise Http404("Tipo de persona no válido")
    
    def get_form_class(self):
        config = self.get_model_and_config()
        return config['form_class']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = self.get_model_and_config()
        
        context['person_type'] = self.kwargs.get('person_type')
        context['form_type'] = config['form_type']
        
        return context
    
    def form_valid(self, form):
        config = self.get_model_and_config()
        obj = form.save()
        name = config['name_field'](obj)
        messages.success(self.request, f'{config["form_type"]} {name} agregado correctamente')
        return redirect(config['detail_url'], person_type=self.kwargs.get('person_type'), pk=obj.pk)
    
    def form_invalid(self, form):
        config = self.get_model_and_config()
        messages.error(self.request, f'Error al crear el {config["form_type"].lower()}')
        return super().form_invalid(form)


class PersonUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/account-update.html'
    
    def get_model_and_config(self):
        """Retorna el modelo, form y configuración según el tipo"""
        person_type = self.kwargs.get('person_type')
        
        if person_type == 'client':
            return {
                'model': Client,
                'form_class': ClientForm,
                'form_type': 'Cliente',
                'detail_url': 'DetailPerson',
                'name_field': lambda obj: f'{obj.first_name} {obj.last_name}'
            }
        elif person_type == 'supplier':
            return {
                'model': Supplier,
                'form_class': SupplierForm,
                'form_type': 'Proveedor',
                'detail_url': 'DetailPerson',
                'name_field': lambda obj: obj.company
            }
        else:
            raise Http404("Tipo de persona no válido")
    
    def get_queryset(self):
        config = self.get_model_and_config()
        return config['model'].objects.all()
    
    def get_form_class(self):
        config = self.get_model_and_config()
        return config['form_class']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = self.get_model_and_config()
        
        context['person_type'] = self.kwargs.get('person_type')
        context['form_type'] = config['form_type']
        
        return context
    
    def form_valid(self, form):
        config = self.get_model_and_config()
        obj = form.save()
        name = config['name_field'](obj)
        messages.success(self.request, f'{config["form_type"]} {name} actualizado correctamente')
        return redirect(config['detail_url'], person_type=self.kwargs.get('person_type'), pk=obj.pk)
    
    def form_invalid(self, form):
        config = self.get_model_and_config()
        messages.error(self.request, f'Error al actualizar el {config["form_type"].lower()}')
        return super().form_invalid(form)


class PersonDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'accounts/account-delete.html'
    
    def get_model_and_config(self):
        """Retorna el modelo y configuración según el tipo"""
        person_type = self.kwargs.get('person_type')
        
        if person_type == 'client':
            return {
                'model': Client,
                'success_url': 'ListPerson',
                'form_type': 'clientes',
                'name_field': lambda obj: f'{obj.first_name} {obj.last_name}'
            }
        elif person_type == 'supplier':
            return {
                'model': Supplier,
                'success_url': 'ListPerson',
                'form_type': 'proveedores',
                'name_field': lambda obj: obj.company
            }
        else:
            raise Http404("Tipo de persona no válido")
    
    def get_queryset(self):
        config = self.get_model_and_config()
        return config['model'].objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['person_type'] = self.kwargs.get('person_type')
        
        # Agregar form_type para el título
        if self.kwargs.get('person_type') == 'client':
            context['form_type'] = 'Cliente'
        else:
            context['form_type'] = 'Proveedor'
        
        return context
    
    def get_success_url(self):
        config = self.get_model_and_config()
        return reverse_lazy(config['success_url'], kwargs={'person_type': self.kwargs.get('person_type')})
    
    def form_valid(self, form):
        config = self.get_model_and_config()
        obj = self.get_object()
        name = config['name_field'](obj)
        messages.success(self.request, f'{name} se ha eliminado de la lista de {config["form_type"]}')
        return super().form_valid(form)


#-------[ VISTAS CLIENTES (mantener compatibilidad) ]-------
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    context_object_name = 'clients'
    template_name = 'accounts/client-list.html'
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
    template_name = 'accounts/client-create.html'

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
    template_name = 'accounts/supplier-list.html'
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
    template_name = 'accounts/supplier-create.html'

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

