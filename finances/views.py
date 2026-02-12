import json
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import models
from django.utils import timezone
from finances.forms import *
from finances.models import *
from accounts.models import CurrentAccount
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
    paginate_by = 10  # NÃºmero de ventas por pÃ¡gina

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
    success_url = reverse_lazy('Sales')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['form_type'] = 'Venta'

        #Lista de productos para el datalist. 
        products = Product.objects.all()
        data['products'] = products

        data['products_json'] = json.dumps(
            [{'name': product.name, 'price': str(product.price)} for product in products]
        )
        
        # Agregar clientes y proveedores para el datalist
        from accounts.models import Client, Supplier
        data['clients'] = Client.objects.all()
        data['suppliers'] = Supplier.objects.all()
        
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
        person_id = self.request.POST.get('person')  # Obtener directamente del POST
        person = None
        
        # Si hay person_id, obtener el objeto Person y guardar su nombre en temporal_name
        if person_id:
            try:
                person = Person.objects.get(pk=person_id)
                form.instance.person = person  # Asignar manualmente
                
                # Guardar el nombre en temporal_name para facilitar búsquedas y visualización
                from accounts.models import Client, Supplier
                try:
                    client = Client.objects.get(pk=person_id)
                    form.instance.temporal_name = f"{client.first_name} {client.last_name}"
                except Client.DoesNotExist:
                    try:
                        supplier = Supplier.objects.get(pk=person_id)
                        form.instance.temporal_name = supplier.company
                    except Supplier.DoesNotExist:
                        pass
                        
            except Person.DoesNotExist:
                pass
        
        items_json = self.request.POST.get('items_json')

        #Procesar los ítems del JSON
        try:
            items = json.loads(items_json)
        except json.JSONDecodeError:
            messages.error(self.request, "Error al procesar los ítems.")
            return self.render_to_response(self.get_context_data(form=form))

        #Guardar venta
        self.object = form.save()

        #creaciÃ³n del item
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

        #Si hay persona vinculada, crear/obtener CurrentAccount
        if person:
            current_account, created = CurrentAccount.objects.get_or_create(
                person=person,
                defaults={'notes': f'Cuenta creada automáticamente el {timezone.now().strftime("%d/%m/%Y")}'}
            )
            self.object.current_account = current_account
            self.object.save()
            
            if created:
                messages.info(self.request, f"Cuenta corriente creada para {person}")

        messages.success(self.request, f"Venta {self.object.ticket_code} agregada correctamente")
        return redirect(self.success_url)
    

class SaleUpdateView(LoginRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleUpdateForm
    template_name = 'finances/ticket-update.html'
    success_url = reverse_lazy('Tickets')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['form_type'] = 'Venta'
        data['sale'] = self.object
        
        # Lista de productos para el datalist
        products = Product.objects.all()
        data['products'] = products
        
        # Agregar clientes y proveedores para búsqueda
        from accounts.models import Client, Supplier
        data['clients'] = Client.objects.all()
        data['suppliers'] = Supplier.objects.all()
        
        return data
    
    def form_valid(self, form):
        # Obtener person_id del POST (puede haber cambiado)
        person_id = self.request.POST.get('person')
        person = None
        
        # Si hay person_id, actualizar la persona asociada
        if person_id:
            try:
                person = Person.objects.get(pk=person_id)
                form.instance.person = person
                
                # Actualizar temporal_name con el nuevo nombre
                from accounts.models import Client, Supplier
                try:
                    client = Client.objects.get(pk=person_id)
                    form.instance.temporal_name = f"{client.first_name} {client.last_name}"
                except Client.DoesNotExist:
                    try:
                        supplier = Supplier.objects.get(pk=person_id)
                        form.instance.temporal_name = supplier.company
                    except Supplier.DoesNotExist:
                        pass
                        
            except Person.DoesNotExist:
                messages.error(self.request, "Persona no encontrada")
                return self.form_invalid(form)
        
        # Obtener items_json del POST
        items_json = self.request.POST.get('items_json')
        
        # Procesar los ítems del JSON
        try:
            items_data = json.loads(items_json)
        except (json.JSONDecodeError, TypeError):
            messages.error(self.request, "Error al procesar los ítems.")
            return self.render_to_response(self.get_context_data(form=form))
        
        if not items_data:
            messages.error(self.request, "Debes agregar al menos un ítem.")
            return self.render_to_response(self.get_context_data(form=form))
        
        # Guardar la venta con los nuevos datos
        self.object = form.save()
        
        # Eliminar items existentes
        Item.objects.filter(sale=self.object).delete()
        
        # Crear nuevos items
        for item_data in items_data:
            product_obj = Product.objects.filter(name=item_data['product_name']).first()
            
            Item.objects.create(
                sale=self.object,
                product=product_obj,
                product_name_cache=item_data['product_name'],
                quantity=item_data['quantity'],
                price=item_data['price'],
            )
        
        # Recalcular total
        self.object.calculate_total()
        
        # Si hay persona vinculada, actualizar CurrentAccount
        if person:
            current_account, created = CurrentAccount.objects.get_or_create(
                person=person,
                defaults={'notes': f'Cuenta creada automáticamente el {timezone.now().strftime("%d/%m/%Y")}'}
            )
            self.object.current_account = current_account
            self.object.save()
            
            if created:
                messages.info(self.request, f"Cuenta corriente creada para {person}")
        
        messages.success(self.request, f"Venta {self.object.ticket_code} actualizada correctamente")
        return redirect(self.success_url)


def cancel_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    sale.status = 'CA'  # Set the status to 'CA' for 'Canceled'
    sale.save()
    messages.success(request, 'Venta cancelada correctamente')
    return redirect('Tickets')


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
    success_url = reverse_lazy('Purchases')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['form_type'] = 'Compra'

        #Lista de productos para el datalist. 
        products = Product.objects.all()
        data['products'] = products

        data['products_json'] = json.dumps(
            [{'name': product.name, 'price': str(product.price)} for product in products]
        )
        
        # Agregar clientes y proveedores para el datalist
        from accounts.models import Client, Supplier
        data['clients'] = Client.objects.all()
        data['suppliers'] = Supplier.objects.all()
        
        return data
    
    def form_valid(self, form):
        #usuario creador
        form.instance.user_created = self.request.user

        #NumTicket 
        type = 'P'
        year = datetime.now().year
        last = NumTicket.objects.filter(type=type, year=year).order_by('-number').first()
        next_number = 1 if not last else last.number + 1
        num_ticket = NumTicket.objects.create(type=type, year=year, number=next_number)

        #asignacion numTicket a compra
        form.instance.ticket_code = num_ticket 

        #Obtener datos del formulario
        temporal_name = form.cleaned_data.get('temporal_name')
        person = form.cleaned_data.get('person')
        items_json = self.request.POST.get('items_json')

        #Procesar los Ã­tems del JSON
        try:
            items = json.loads(items_json)
        except json.JSONDecodeError:
            messages.error(self.request, "Error al procesar los Ã­tems.")
            return self.render_to_response(self.get_context_data(form=form))

        #Guardar compra
        self.object = form.save()

        #creaciÃ³n del item
        for item_data in items:
            product_obj = Product.objects.filter(name=item_data['product_name']).first()

            Item.objects.create(
                purchase=self.object,
                product=product_obj,
                product_name_cache=item_data['product_name'],
                quantity=item_data['quantity'],
                price=item_data['price'],
            )

        self.object.calculate_total()

        #Si hay persona vinculada, crear/obtener CurrentAccount
        if person:
            current_account, created = CurrentAccount.objects.get_or_create(
                person=person,
                defaults={'notes': f'Cuenta creada automáticamente el {timezone.now().strftime("%d/%m/%Y")}'}
            )
            self.object.current_account = current_account
            self.object.save()
            
            if created:
                messages.info(self.request, f"Cuenta corriente creada para {person}")

        messages.success(self.request, f'Compra {self.object.ticket_code} agregada correctamente')
        return redirect(self.success_url)
        

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
            messages.success(self.request, 'Compra actualizada correctamente')
            return redirect(self.success_url)
        else:
            messages.error(self.request, 'Error al actualizar la compra')
            return self.form_invalid(form)
        
        
class PurchaseDeleteView(LoginRequiredMixin, DeleteView):
    model = Purchase
    template_name = 'finances/ticket-delete.html'
    success_url = reverse_lazy('Tickets')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Compra eliminada correctamente')
        return super().delete(request, *args, **kwargs)


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
    success_url = reverse_lazy('Payments')
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['form_type'] = 'Pago'
        
        # Agregar clientes y proveedores para el datalist
        from accounts.models import Client, Supplier
        data['clients'] = Client.objects.all()
        data['suppliers'] = Supplier.objects.all()
        
        return data
    
    def form_valid(self, form):
        #usuario creador
        form.instance.user_created = self.request.user

        #NumTicket 
        type = 'PA'
        year = datetime.now().year
        last = NumTicket.objects.filter(type=type, year=year).order_by('-number').first()
        next_number = 1 if not last else last.number + 1
        num_ticket = NumTicket.objects.create(type=type, year=year, number=next_number)

        #asignacion numTicket a pago
        form.instance.ticket_code = num_ticket 

        #Obtener persona vinculada
        person = form.cleaned_data.get('person')

        #Guardar pago
        payment = form.save()

        #Si hay persona vinculada, crear/obtener CurrentAccount y vincular
        if person:
            current_account, created = CurrentAccount.objects.get_or_create(
                person=person,
                defaults={'notes': f'Cuenta creada automáticamente el {timezone.now().strftime("%d/%m/%Y")}'}
            )
            payment.current_account = current_account
            payment.save()
            
            if created:
                messages.info(self.request, f"Cuenta corriente creada para {person}")

        messages.success(self.request, f'Pago {payment.ticket_code} agregado correctamente')
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el pago')
        return super().form_invalid(form)


class PaymentUpdateView(LoginRequiredMixin, UpdateView):
    model = Payment
    form_class = PaymentCreateForm
    template_name = 'finances/ticket-update.html'
    success_url = reverse_lazy('Tickets')
    
    def form_valid(self, form):
        messages.success(self.request, 'Pago actualizado correctamente')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el pago')
        return super().form_invalid(form)




class PaymentDeleteView(LoginRequiredMixin, DeleteView):
    model = Payment
    template_name = 'finances/ticket-delete.html'
    success_url = reverse_lazy('Tickets')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Pago eliminado correctamente')
        return super().delete(request, *args, **kwargs)


#---------------------------------
#CREDIT NOTES

class CreditNoteListView(LoginRequiredMixin, ListView):
    model = CreditNote
    context_object_name = 'tickets'
    template_name = 'finances/ticket-list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'Notas de Credito'
        context['update_url'] = 'UpdateCreditNote'
        context['detail_url'] = 'DetailCreditNote'
        context['cancel_url'] = 'DeleteCreditNote'
        return context

class CreditNoteDetailView(LoginRequiredMixin, DetailView):
    model = CreditNote
    template_name = 'finances/ticket-detail.html'
    context_object_name = 'creditnote'

class CreditNoteCreateView(LoginRequiredMixin, CreateView):
    model = CreditNote
    form_class = CreditNoteCreateForm
    template_name = 'finances/ticket-create.html'
    success_url = reverse_lazy('CreditNotes')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['form_type'] = 'Nota de Credito'
        
        # Agregar clientes y proveedores para el datalist
        from accounts.models import Client, Supplier
        data['clients'] = Client.objects.all()
        data['suppliers'] = Supplier.objects.all()
        
        return data

    def form_valid(self, form):
        form.instance.user_created = self.request.user
        type = 'CN'
        year = datetime.now().year
        last = NumTicket.objects.filter(type=type, year=year).order_by('-number').first()
        next_number = 1 if not last else last.number + 1
        num_ticket = NumTicket.objects.create(type=type, year=year, number=next_number)
        form.instance.ticket_code = num_ticket
        person = form.cleaned_data.get('person')
        note_type = form.cleaned_data.get('note_type')
        credit_note = form.save()
        
        if person:
            current_account, created = CurrentAccount.objects.get_or_create(
                person=person,
                defaults={'notes': f'Cuenta creada automáticamente el {timezone.now().strftime("%d/%m/%Y")}'}
            )
            credit_note.current_account = current_account
            credit_note.save()
            
            if created:
                messages.info(self.request, f'Cuenta corriente creada para {person}')
        
        messages.success(self.request, f'Nota de Credito {credit_note.ticket_code} agregada correctamente')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la nota de credito')
        return super().form_invalid(form)

class CreditNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = CreditNote
    form_class = CreditNoteCreateForm
    template_name = 'finances/ticket-update.html'
    success_url = reverse_lazy('Tickets')

    def form_valid(self, form):
        messages.success(self.request, 'Nota de Credito actualizada correctamente')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar la nota de credito')
        return super().form_invalid(form)

class CreditNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = CreditNote
    template_name = 'finances/ticket-delete.html'
    success_url = reverse_lazy('Tickets')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Nota de Credito eliminada correctamente')
        return super().delete(request, *args, **kwargs)


#-------[ VISTAS CUENTA CORRIENTE ]-------
class CurrentAccountDetailView(LoginRequiredMixin, DetailView):
    model = CurrentAccount
    template_name = 'finances/current-account-detail.html'
    context_object_name = 'account'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['balance'] = self.object.get_balance()
        context['ledger'] = self.object.get_ledger()
        context['transactions'] = self.object.get_transactions()
        return context


class CurrentAccountListView(LoginRequiredMixin, ListView):
    model = CurrentAccount
    template_name = 'finances/current-account-list.html'
    context_object_name = 'accounts'
    paginate_by = 20
    
    def get_queryset(self):
        qs = CurrentAccount.objects.select_related('person').all()
        search = self.request.GET.get('search', '')
        
        if search:
            from accounts.models import Client, Supplier
            # Buscar en clientes y proveedores
            qs = qs.filter(
                models.Q(person__client__first_name__icontains=search) |
                models.Q(person__client__last_name__icontains=search) |
                models.Q(person__supplier__company__icontains=search)
            )
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar balance a cada cuenta
        accounts_with_balance = []
        for account in context['accounts']:
            accounts_with_balance.append({
                'account': account,
                'balance': account.get_balance(),
                'person_name': str(account.person)
            })
        context['accounts_with_balance'] = accounts_with_balance
        context['search'] = self.request.GET.get('search', '')
        return context


@login_required
def current_account_by_person(request, person_id):
    """Vista para acceder a cuenta corriente por person_id, creándola si no existe"""
    from accounts.models import Person
    
    person = get_object_or_404(Person, pk=person_id)
    
    # Obtener o crear la cuenta corriente
    current_account, created = CurrentAccount.objects.get_or_create(
        person=person,
        defaults={'notes': f'Cuenta creada automáticamente el {timezone.now().strftime("%d/%m/%Y")}'}
    )
    
    # Obtener datos para el template
    balance = current_account.get_balance()
    ledger = current_account.get_ledger()
    transactions = current_account.get_transactions()
    
    return render(request, 'finances/current-account-detail.html', {
        'account': current_account,
        'balance': balance,
        'ledger': ledger,
        'transactions': transactions
    })
