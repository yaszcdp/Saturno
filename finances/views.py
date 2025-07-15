import json
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from finances.forms import *
from finances.models import *
from products.models import Product
from django.contrib import messages
from datetime import datetime

# Create your views here.
@login_required
def register_view(request):
    return render(request, 'finances/register.html')

#-------[ VISTAS CAJA ]-------
@login_required
def init_register_view(request):
    if request.method == 'POST':
        form = CashRegisterForm(request.POST)

        if form.is_valid():
            cash_register = form.save(commit=False)
            cash_register.init_register(form.cleaned_data['initial_amounts'])
            cash_register.save()
            return redirect('Register')
    else:
        form = CashRegisterForm()
    return render(request, 'finances/register_init.html', {'form': form})

@login_required
def close_register_view(request):
    if request.method == 'POST':
        form = CashRegisterForm(request.POST)

        if form.is_valid():
            cash_register = form.save(commit=False)
            cash_register.close_register(form.cleaned_data['final_amounts'])
            cash_register.save()
            return redirect('Register')
    else:
        form = CashRegisterForm()
    return render(request, 'finances/register_close.html', {'form': form})


#-------[ VISTAS TICKETS ]-------
@login_required
def tickets_view(request):
    return render(request, 'finances/tickets.html')

#---------------------------------
#SALES

class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    context_object_name = 'tickets'
    template_name = 'finances/ticket-list.html'
    paginate_by = 10  # Número de ventas por página

    def get_queryset(self):
        qs = Sale.objects.all().order_by('-date_time')
        search_by = self.request.GET.get('search_by', '')
        query = self.request.GET.get('query', '')
        date = self.request.GET.get('date', '')

        if not search_by and query:
            return Sale.objects.none()
        else:
            if search_by == 'client' and query:
                qs = qs.filter(temporal_name__icontains=query)
            elif search_by == 'user' and query:
                qs = qs.filter(user_created__username__icontains=query)
            elif search_by == 'date' and date:
                qs = qs.filter(date_time__date=date)
            elif search_by == 'code' and query:
                qs = qs.filter(ticket_code__code__icontains=query)
        
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'Ventas'
        context['search_by'] = self.request.GET.get('search_by', '')
        context['search_options']=[
            {'value': 'client', 'label': 'Cliente'},
            {'value': 'user', 'label': 'Usuario'},
            {'value': 'date', 'label': 'Fecha'},
            {'value': 'code', 'label': 'Nro de Comprobante'}
        ]
        context['query'] = self.request.GET.get('query', '')
        context['date'] = self.request.GET.get('date', '')
        context['no_results'] = not context['tickets'].exists()

        #context['update_url'] = 'UpdateSale'
        #context['detail_url'] = 'DetailSale'
        #context['cancel_url'] = 'CancelSale'
        params = self.request.GET.copy()
        if params.get('page'):
            del params['page']      
            context['params'] = params.urlencode()
        return context
    


class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'finances/ticket-detail.html'
    context_object_name = 'sale'


class SaleCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SaleCreateForm
    template_name = 'finances/ticket-create.html'
    success_url = reverse_lazy('Tickets')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['form_type'] = 'Venta'

        #Lista de productos para el datalist. 
        products = Product.objects.all()
        data['products'] = products

        data['products_json'] = json.dumps(
            [{'name': product.name, 'price': str(product.price)} for product in products]
        )
        
        return data
    
    def form_valid(self, form):
        #usuario creador
        form.instance.user_created = self.request.user

        #NumTicket 
        type = 'S'
        year = datetime.now().year
        last = NumTicket.objects.filter(type=type, year=year).order_by('-number').first()
        next_number = 1 if not last else last.number + 1
        num_ticket = NumTicket.objects.create(type=type, year=year, number=next_number)

        #asignacion numTicket a venta
        form.instance.ticket_code = num_ticket 

        #Obtener datos del formulario
        temporal_name = form.cleaned_data.get('temporal_name')
        print(f"Temporal Name: {temporal_name} ")
        items_json = self.request.POST.get('items_json')
        print(f"Items JSON: {items_json} ")

        #Procesar los ítems del JSON
        try:
            items = json.loads(items_json)
            print(f"Items: {items} ")
        except json.JSONDecodeError:
            messages.error(self.request, "Error al procesar los ítems.")
            return self.render_to_response(self.get_context_data(form=form))

        #Guardar venta
        self.object = form.save()

        #creación del item
        for item_data in items:
            product_obj = Product.objects.filter(name=item_data['product_name']).first()

            Item.objects.create(
                sale=self.object,
                product=product_obj,
                product_name_cache=item_data['product_name'],
                quantity=item_data['quantity'],
                price=item_data['price'],
            )

        self.object.calculate_total()

        messages.success(self.request, "¡Venta creada con éxito!")
        return self.render_to_response(self.get_context_data(form=form))
    

class SaleUpdateView(LoginRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleUpdateForm
    template_name = 'finances/ticket-update.html'
    success_url = reverse_lazy('Tickets')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = SaleItemFormSet(self.request.POST, instance=self.object)
        else:
            data['formset'] = SaleItemFormSet(instance=self.object)
        return data
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


def cancel_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    sale.status = 'CA'  # Set the status to 'CA' for 'Canceled'
    sale.save()
    return render(request, 'finances/ticket-list.html')


#---------------------------------
#PURCHASES

class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    context_object_name = 'tickets'
    template_name = 'finances/ticket-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'Compras'
        context['update_url'] = 'UpdatePurchase'
        context['detail_url'] = 'DetailPurchase'
        context['cancel_url'] = 'CancelPurchase'

class PurchaseDetailView(LoginRequiredMixin, DetailView):
    model = Purchase
    template_name = 'finances/ticket-detail.html'
    context_object_name = 'purchase'


class PurchaseCreateView(LoginRequiredMixin, CreateView):
    model = Purchase
    form_class = PurchaseCreateForm
    template_name = 'finances/ticket-create.html'
    success_url = reverse_lazy('Tickets')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = PurchaseItemFormSet(self.request.POST)
        else:
            data['formset'] = PurchaseItemFormSet()
        return data
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)
        

class PurchaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Purchase
    form_class = PurchaseCreateForm
    template_name = 'finances/ticket-update.html'
    success_url = reverse_lazy('Tickets')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = PurchaseItemFormSet(self.request.POST, instance=self.object)
        else:
            data['formset'] = PurchaseItemFormSet(instance=self.object)
        return data
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)
        
        
class PurchaseDeleteView(LoginRequiredMixin, DeleteView):
    model = Purchase
    template_name = 'finances/ticket-delete.html'
    success_url = reverse_lazy('Tickets')


#---------------------------------
#PAYMENTS

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    context_object_name = 'pagos'
    template_name = 'finances/ticket-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'Pagos'
        context['update_url'] = 'UpdatePayment'
        context['detail_url'] = 'DetailPayment'
        context['cancel_url'] = 'CancelPayment'


class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'finances/ticket-detail.html'
    context_object_name = 'payment'


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentCreateForm
    template_name = 'finances/ticket-create.html'
    success_url = reverse_lazy('Tickets')


class PaymentUpdateView(LoginRequiredMixin, UpdateView):
    model = Payment
    form_class = PaymentCreateForm
    template_name = 'finances/ticket-update.html'
    success_url = reverse_lazy('Tickets')


class PaymentDeleteView(LoginRequiredMixin, DeleteView):
    model = Payment
    template_name = 'finances/ticket-delete.html'
    success_url = reverse_lazy('Tickets')