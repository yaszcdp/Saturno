from django import forms
from products.models import Product, ProductBatch
from accounts.models import Supplier

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'unit', 'price']
        labels = {
            'name': 'Nombre',
            'category': 'Categoría',
            'unit': 'Unidad',
            'price': 'Precio referencia',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ProductBatchForm(forms.ModelForm):
    # Campo para elegir entre producto existente o crear nuevo
    product_option = forms.ChoiceField(
        choices=[('existing', 'Agregar a existente'), ('new', 'Crear nuevo')],
        widget=forms.RadioSelect,
        label='Opción',
        initial='existing'
    )
    
    # Campo para buscar proveedor (será manejado con datalist en el template)
    supplier_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    class Meta:
        model = ProductBatch
        fields = ['product', 'entry_date', 'initial_quantity', 'base_price', 
                 'transport_cost', 'entry_cost', 'cost_per_unit', 'suggested_price', 'notes']
        labels = {
            'product': 'Producto',
            'entry_date': 'Fecha de ingreso',
            'initial_quantity': 'Cantidad',
            'base_price': 'Precio base',
            'transport_cost': 'Costo flete',
            'entry_cost': 'Costo entradas',
            'cost_per_unit': 'Precio costo unitario',
            'suggested_price': 'Precio sugerido venta',
            'notes': 'Notas',
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'entry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'initial_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_base_price'}),
            'transport_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_transport_cost'}),
            'entry_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_entry_cost'}),
            'cost_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_cost_per_unit', 'readonly': True}),
            'suggested_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que cost_per_unit sea readonly ya que se calcula automáticamente
        self.fields['cost_per_unit'].required = False
