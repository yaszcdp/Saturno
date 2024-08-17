from django import forms
from accounts.models import CurrentAccount
from finances.models import CashRegister, Sale, Payment, Purchase, Item
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

#SALES
class SaleCreateForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['temporal_name']
        labels = {'temporal_name': 'Nombre Temporal'}

class SaleUpdateForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['temporal_name', 'status', 'payment_method', 'current_account']
        labels = {
            'temporal_name': 'Nombre Temporal', 
            'status': 'Estado', 
            'payment_method': 'Método de Pago',
            'current_account': 'Cuenta Corriente'
        }

#PURCHASES
class PurchaseCreateForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['temporal_name']
        labels = {'temporal_name': 'Nombre Temporal'}

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
SaleItemFormSet = inlineformset_factory(Sale, Item, form=ItemCreateForm, extra=1, can_delete=True)
PurchaseItemFormSet = inlineformset_factory(Purchase, Item, form=ItemCreateForm, extra=1, can_delete=True)

#PAYMENTS
class PaymentCreateForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_type', 'current_account']
        labels = {
            'amount': 'Monto',
            'payment_type': 'Tipo de Pago',
            'current_account': 'Cuenta'
        }