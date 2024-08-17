from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from finances.forms import *
from finances.models import *

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'Ventas'
        context['update_url'] = 'UpdateSale'
        context['detail_url'] = 'DetailSale'
        context['cancel_url'] = 'CancelSale'
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
        if self.request.POST:
            data['formset'] = SaleItemFormSet(self.request.POST, instance=self.object)
            print('Entró en el if', self.request.POST)
        else:
            data['formset'] = SaleItemFormSet(instance=self.object)
            print('No entró')
        return data
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object.save()
            formset.instance = self.object
            formset.save()

            self.object.calculate_total()
            self.object.save()

            return redirect(self.success_url)
        else:
            return self.form_invalid(form)
    

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