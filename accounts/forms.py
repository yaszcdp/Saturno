from django import forms
from accounts.models import Client, Supplier, CurrentAccount

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'cuit', 'phone']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'cuit': 'Cuit',
            'phone': 'Teléfono'
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['company', 'cuit', 'phone']
        labels = {
            'company': 'Empresa',
            'cuit': 'Cuit',
            'phone': 'Teléfono'
        }