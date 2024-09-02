from django.shortcuts import render
from django.http import HttpResponse
from accounts.models import *
from userManagement.models import *

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def search(request):
    query = request.GET.get('query', '')
    page = request.GET.get('page', '')

    if page == 'Users':
        users = User.objects.filter(first_name__icontains=query) | User.objects.filter(last_name__icontains=query)
        return render(request, 'userManagement/user-list.html', {'users': users})
    elif page == 'Clients':
        clients = Client.objects.filter(first_name__icontains=query) | Client.objects.filter(last_name__icontains=query)
        return render(request, 'accounts/client-list.html', {'clients': clients})
    elif page == 'Suppliers':
        suppliers = Supplier.objects.filter(company__icontains=query)
        return render(request, 'accounts/Supplier-list.html', {'suppliers': suppliers})
    else:
        response = "No hay resultados"
        return HttpResponse(response)
