from django.db import models
from accounts.models import Person, Supplier

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    category = models.CharField(max_length=100, null=True, blank=True, verbose_name='Categoría')
    unit = models.CharField(max_length=50, null=True, blank=True, verbose_name='Unidad', 
                           help_text='Ej: cajón, kg, unidad')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio referencia')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_total_stock(self):
        """Calcula el stock total sumando todos los lotes activos"""
        return sum(batch.current_stock for batch in self.batches.all())


class ProductBatch(models.Model):
    """Representa un lote/ingreso de mercadería"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches', 
                                verbose_name='Producto')
    supplier = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True,
                                 limit_choices_to={'supplier__isnull': False},
                                 verbose_name='Proveedor')
    
    # Fechas
    entry_date = models.DateField(verbose_name='Fecha de ingreso')
    
    # Cantidades
    initial_quantity = models.DecimalField(max_digits=10, decimal_places=2, 
                                          verbose_name='Cantidad inicial')
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, 
                                       verbose_name='Stock actual')
    losses = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                verbose_name='Pérdidas acumuladas')
    
    # Costos
    base_price = models.DecimalField(max_digits=10, decimal_places=2,
                                    verbose_name='Precio base',
                                    help_text='Precio acordado con proveedor')
    transport_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                        verbose_name='Costo de flete')
    entry_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                    verbose_name='Costo de entradas')
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2,
                                       verbose_name='Precio costo unitario',
                                       help_text='Costo final por unidad (incluye todos los gastos)')
    
    # Precio sugerido venta
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2,
                                         verbose_name='Precio sugerido de venta')
    
    # Relaciones opcionales
    related_purchase = models.ForeignKey('finances.Ticket', on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='product_batches',
                                        verbose_name='Compra relacionada')
    
    # Notas
    notes = models.TextField(null=True, blank=True, verbose_name='Notas')
    
    class Meta:
        verbose_name = 'Lote de producto'
        verbose_name_plural = 'Lotes de productos'
        ordering = ['-entry_date', 'product__name']
    
    def __str__(self):
        return f"{self.product.name} - {self.entry_date} ({self.current_stock}/{self.initial_quantity})"
    
    def save(self, *args, **kwargs):
        # Si es nuevo, el stock actual es igual a la cantidad inicial
        if not self.pk:
            self.current_stock = self.initial_quantity
        super().save(*args, **kwargs)
    
    def get_sold_quantity(self):
        """Calcula la cantidad vendida del lote"""
        return self.initial_quantity - self.current_stock - self.losses

