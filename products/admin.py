from django.contrib import admin
from products.models import Product, ProductBatch


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'price', 'get_total_stock']
    list_filter = ['category']
    search_fields = ['name', 'category']
    
    def get_total_stock(self, obj):
        return obj.get_total_stock()
    get_total_stock.short_description = 'Stock Total'


@admin.register(ProductBatch)
class ProductBatchAdmin(admin.ModelAdmin):
    list_display = ['product', 'supplier', 'entry_date', 'initial_quantity', 
                   'current_stock', 'losses', 'cost_per_unit', 'suggested_price']
    list_filter = ['entry_date', 'product', 'supplier']
    search_fields = ['product__name', 'supplier__company']
    date_hierarchy = 'entry_date'
    readonly_fields = ['current_stock']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('product', 'supplier', 'entry_date')
        }),
        ('Cantidades', {
            'fields': ('initial_quantity', 'current_stock', 'losses')
        }),
        ('Costos', {
            'fields': ('base_price', 'transport_cost', 'entry_cost', 'cost_per_unit')
        }),
        ('Venta', {
            'fields': ('suggested_price',)
        }),
        ('Relaciones', {
            'fields': ('related_purchase', 'notes'),
            'classes': ('collapse',)
        }),
    )
