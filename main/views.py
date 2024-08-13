from django.shortcuts import render
from userManagement.models import Avatar

def base(request):
    avatar = Avatar.objects.get(user=request.user)
    return render(request, 'main/base.html', {'avatar': avatar})

# Create your views here.
def index(request):
    return render(request, 'main/index.html')