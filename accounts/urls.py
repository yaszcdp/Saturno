from django.urls import path
from accounts import views
from accounts.views import accounts_view

urlpatterns = [
    path('', accounts_view, name='Accounts'),

    path('clientes', views.ClientListView.as_view(), name='Clients'),
    path('ver-cliente/<int:pk>', views.ClientDetailView.as_view(), name='DetailClient'),
    path('nuevo-cliente', views.ClientCreateView.as_view(), name='CreateClient'),
    path('editar-cliente/<int:pk>', views.ClientUpdateView.as_view(), name='UpdateClient'),
    path('eliminar-cliente/<int:pk>', views.ClientDeleteView.as_view(), name='DeleteClient'),

    path('proveedores', views.SupplierListView.as_view(), name='Suppliers'),
    path('ver-proveedor/<int:pk>', views.SupplierDetailView.as_view(), name='DetailSupplier'),
    path('nuevo-proveedor', views.SupplierCreateView.as_view(), name='CreateSupplier'),
    path('editar-proveedor/<int:pk>', views.SupplierUpdateView.as_view(), name='UpdateSupplier'),
    path('eliminar-proveedor/<int:pk>', views.SupplierDeleteView.as_view(), name='DeleteSupplier'),
]