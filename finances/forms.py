from django import forms
from accounts.models import CurrentAccount, Person, Client, Supplier
from finances.models import CashRegister, Sale, Payment, Purchase, Item, CreditNote
from products.models import Product
from django.utils import timezone
from django.forms import inlineformset_factory

#----------------[ CASH REGISTER FORM ]----------------

class CashRegisterForm(forms.ModelForm):
    class Meta:
        model = CashRegister
        fields = ['initial_amounts', 'final_amounts']

    def __init__(self, *args, **kwargs):
        #Inicializa la caja registradora, si hay un registro anterior lo toma como monto inicial
        super().__init__(*args, **kwargs)
        previous_register = CashRegister.objects.filter(status='C').order_by('-date').first()
        
        if previous_register:
            self.fields['initial_amounts'].initial = previous_register.final_amounts

#----------------[ TICKETS FORMS ]----------------
class BaseSaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = '__all__'
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'current_account': forms.Select(attrs={'class': 'form-select'}),
        }

class SaleCreateForm(BaseSaleForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        required=False,
        empty_label="Seleccionar Cliente/Proveedor",
        label='Cliente/Proveedor',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta(BaseSaleForm.Meta):
        fields = ['person', 'temporal_name']
        labels = {
            'person': 'Cliente/Proveedor',
            'temporal_name': 'Nombre (si no está en lista)'
        }
        widgets = {
            'temporal_name': forms.TextInput(attrs={'placeholder': 'Nombre temporal del cliente'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar el queryset para mostrar nombres más descriptivos
        clients = Client.objects.all()
        suppliers = Supplier.objects.all()
        
        # Crear lista personalizada con etiquetas
        choices = [('', 'Seleccionar Cliente/Proveedor')]
        if clients.exists():
            choices.append(('Clientes', [(c.person_ptr_id, f'Cliente: {c}') for c in clients]))
        if suppliers.exists():
            choices.append(('Proveedores', [(s.person_ptr_id, f'Proveedor: {s}') for s in suppliers]))
        
        self.fields['person'].choices = choices

class SaleUpdateForm(BaseSaleForm):
    class Meta(BaseSaleForm.Meta):
        fields = ['payment_status', 'payment_method', 'temporal_name']
        labels = {
            'payment_status': 'Estado de Pago',
            'payment_method': 'Método de Pago',
            'temporal_name': 'Nombre del Cliente'
        }
        widgets = {
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'temporal_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
        }





''''
#SALES
#Formulario creacion para vendedores. Asignan items y nombre cliente. 
class SaleCreateForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['temporal_name']
        labels = {'temporal_name': 'Nombre Cliente'}

#Formulario de actualización para cajera. Cambia el estado y asigna metodo de pago o cuenta corriente. 
class SaleUpdateForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['status', 'payment_method', 'current_account']
        labels = {
            'status': 'Estado', 
            'payment_method': 'Método de Pago',
            'current_account': 'Cuenta Corriente'
        }
'''
#PURCHASES
class PurchaseCreateForm(forms.ModelForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        required=False,
        empty_label="Seleccionar Proveedor/Cliente",
        label='Proveedor/Cliente',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Purchase
        fields = ['person', 'temporal_name']
        labels = {
            'person': 'Proveedor/Cliente',
            'temporal_name': 'Nombre (si no está en lista)'
        }
        widgets = {
            'temporal_name': forms.TextInput(attrs={'placeholder': 'Nombre temporal'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Crear lista personalizada con etiquetas
        clients = Client.objects.all()
        suppliers = Supplier.objects.all()
        
        choices = [('', 'Seleccionar Proveedor/Cliente')]
        if suppliers.exists():
            choices.append(('Proveedores', [(s.person_ptr_id, f'Proveedor: {s}') for s in suppliers]))
        if clients.exists():
            choices.append(('Clientes', [(c.person_ptr_id, f'Cliente: {c}') for c in clients]))
        
        self.fields['person'].choices = choices



#ITEMS
class ItemCreateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['product', 'quantity', 'price']
        labels = {
            'product': 'Producto',
            'quantity': 'Cantidad',
            'price': 'Precio'
        }
        widgets = {
            'product': forms.Select(attrs={'placeholder': 'Seleccione un producto'}),
            'quantity': forms.TextInput(attrs={'placeholder': 'Cantidad'}),
            'price': forms.TextInput()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.product:
            self.fields['price'].widget.attrs['placeholder'] = f'{self.instance.product.price}'

#FORMSETS
#SaleItemFormSet = inlineformset_factory(Sale, Item, form=ItemCreateForm, extra=1, can_delete=True)
SaleItemFormSet = forms.inlineformset_factory(
    parent_model = Sale, 
    model = Item, 
    fields = ('product', 'quantity', 'price'), 
    extra = 1, 
    can_delete = True,
)


PurchaseItemFormSet = inlineformset_factory(Purchase, Item, form=ItemCreateForm, extra=1, can_delete=True)

#PAYMENTS
class PaymentCreateForm(forms.ModelForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        required=False,
        empty_label="Seleccionar Cliente/Proveedor",
        label='Cliente/Proveedor',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Payment
        fields = ['person', 'amount', 'payment_type', 'payment_method']
        labels = {
            'person': 'Cliente/Proveedor',
            'amount': 'Monto',
            'payment_type': 'Tipo de Pago',
            'payment_method': 'Método de Pago'
        }
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Crear lista personalizada con etiquetas
        clients = Client.objects.all()
        suppliers = Supplier.objects.all()
        
        choices = [('', 'Seleccionar Cliente/Proveedor')]
        if clients.exists():
            choices.append(('Clientes', [(c.person_ptr_id, f'Cliente: {c}') for c in clients]))
        if suppliers.exists():
            choices.append(('Proveedores', [(s.person_ptr_id, f'Proveedor: {s}') for s in suppliers]))
        
        self.fields['person'].choices = choices


#CREDIT NOTES
class CreditNoteCreateForm(forms.ModelForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        required=False,
        empty_label="Seleccionar Cliente/Proveedor",
        label='Cliente/Proveedor',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = CreditNote
        fields = ['person', 'note_type', 'description', 'amount']
        labels = {
            'person': 'Cliente/Proveedor',
            'note_type': 'Tipo',
            'description': 'Descripción/Motivo',
            'amount': 'Monto'
        }
        widgets = {
            'note_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción o motivo de la nota de crédito'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Crear lista personalizada con etiquetas
        clients = Client.objects.all()
        suppliers = Supplier.objects.all()
        
        choices = [('', 'Seleccionar Cliente/Proveedor')]
        if clients.exists():
            choices.append(('Clientes', [(c.person_ptr_id, f'Cliente: {c}') for c in clients]))
        if suppliers.exists():
            choices.append(('Proveedores', [(s.person_ptr_id, f'Proveedor: {s}') for s in suppliers]))
        
        self.fields['person'].choices = choices



