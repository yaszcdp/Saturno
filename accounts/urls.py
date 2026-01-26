from django.urls import path
from accounts import views
from accounts.views import accounts_view

urlpatterns = [
    path('', accounts_view, name='Accounts'),

    # URLs genéricas
    path('<str:person_type>/lista', views.PersonListView.as_view(), name='ListPerson'),
    path('<str:person_type>/ver/<int:pk>', views.PersonDetailView.as_view(), name='DetailPerson'),
    path('<str:person_type>/nuevo', views.PersonCreateView.as_view(), name='CreatePerson'),
    path('<str:person_type>/editar/<int:pk>', views.PersonUpdateView.as_view(), name='UpdatePerson'),
    path('<str:person_type>/eliminar/<int:pk>', views.PersonDeleteView.as_view(), name='DeletePerson'),

    # URLs de compatibilidad (redirigen a las genéricas)
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