from django.urls import path
from finances.views import *
from finances import views

urlpatterns = [
    path('register/', register_view, name='CashRegister'),
    path('register-init/', init_register_view, name='CashRegisterInit'),
    path('register-close/', close_register_view, name='CashRegisterClose'),

    path('tickets/', tickets_view, name='Tickets'),

    path('list-sales/', views.SaleListView.as_view(), name='Sales'),
    path('create-sale/', views.SaleCreateView.as_view(), name='CreateSale'),
    path('detail-sale/<int:pk>/', views.SaleDetailView.as_view(), name='DetailSale'),
    path('update-sale/<int:pk>/', views.SaleUpdateView.as_view(), name='UpdateSale'),
    path('cancel-sale/<int:pk>/', views.cancel_sale, name='CancelSale'),

    path('list-purchases/', views.PurchaseListView.as_view(), name='Purchases'),
    path('create-purchase/', views.PurchaseCreateView.as_view(), name='CreatePurchase'),
    path('detail-purchase/<int:pk>/', views.PurchaseDetailView.as_view(), name='DetailPurchase'),
    path('update-purchase/<int:pk>/', views.PurchaseUpdateView.as_view(), name='UpdatePurchase'),
    path('delete-purchase/<int:pk>/', views.PurchaseDeleteView.as_view(), name='DeletePurchase'),

    path('list-payments/', views.PaymentListView.as_view(), name='Payments'),
    path('create-payment/', views.PaymentCreateView.as_view(), name='CreatePayment'),
    path('detail-payment/<int:pk>/', views.PaymentDetailView.as_view(), name='DetailPayment'),
    path('update-payment/<int:pk>/', views.PaymentUpdateView.as_view(), name='UpdatePayment'),
    path('delete-payment/<int:pk>/', views.PaymentDeleteView.as_view(), name='DeletePayment'),
]