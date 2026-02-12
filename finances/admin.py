from django.contrib import admin
from finances.models import PaymentDetail, Sale

# Register your models here.

@admin.register(PaymentDetail)
class PaymentDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'sale', 'amount', 'payment_method', 'created_at', 'user_created', 'is_reverted']
    list_filter = ['payment_method', 'is_reverted', 'created_at']
    search_fields = ['sale__ticket_code__code', 'notes']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['ticket_code', 'person', 'amount', 'payment_status', 'delivery_status', 'date_time']
    list_filter = ['payment_status', 'delivery_status', 'date_time']
    search_fields = ['ticket_code__code', 'temporal_name']

