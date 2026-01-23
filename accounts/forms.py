from django import forms
from accounts.models import Client, Supplier, CurrentAccount

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'business_name', 'cuit', 'phone', 'city']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'business_name': 'Empresa/Verdulería',
            'cuit': 'Cuit',
            'phone': 'Teléfono',
            'city': 'Ciudad'
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['company', 'salesperson', 'administrator', 'cuit', 'phone', 'city']
        labels = {
            'company': 'Empresa',
            'salesperson': 'Vendedor',
            'administrator': 'Administrativo',
            'cuit': 'Cuit',
            'phone': 'Teléfono',
            'city': 'Ciudad'
        }