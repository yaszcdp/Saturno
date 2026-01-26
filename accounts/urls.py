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
]