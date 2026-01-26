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




