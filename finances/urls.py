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

    path('list-creditnotes/', views.CreditNoteListView.as_view(), name='CreditNotes'),
    path('create-creditnote/', views.CreditNoteCreateView.as_view(), name='CreateCreditNote'),
    path('detail-creditnote/<int:pk>/', views.CreditNoteDetailView.as_view(), name='DetailCreditNote'),
    path('update-creditnote/<int:pk>/', views.CreditNoteUpdateView.as_view(), name='UpdateCreditNote'),
    path('delete-creditnote/<int:pk>/', views.CreditNoteDeleteView.as_view(), name='DeleteCreditNote'),
    
    path('current-accounts/', views.CurrentAccountListView.as_view(), name='CurrentAccounts'),
    path('current-account/<int:pk>/', views.CurrentAccountDetailView.as_view(), name='CurrentAccountDetail'),
    path('current-account/person/<int:person_id>/', views.current_account_by_person, name='CurrentAccountByPerson'),

    path('sale/<int:sale_id>/add-payment/', views.add_payment_detail, name='AddPaymentDetail'),
    path('payment-detail/<int:pd_id>/revert/', views.revert_payment_detail, name='RevertPaymentDetail'),
    path('payment-detail/<int:pd_id>/update/', views.update_payment_detail, name='UpdatePaymentDetail'),
]