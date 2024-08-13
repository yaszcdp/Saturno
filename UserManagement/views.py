from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from userManagement.forms import UserRegisterForm, UserUpdateForm, RoleAssignForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect
from .models import Role, User, Avatar
import django.contrib.messages as messages
from django.conf import settings


#----------------[ User Register ]----------------
def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado con éxito')
            return render(request, 'main/index.html')
        else:
            messages.error(request, 'Error de formulario')
    else:
        form = UserRegisterForm()
    
    return render(request, 'userManagement/user-register.html', {'form': form})


#----------------[ User Login ]----------------
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                messages.success(request, 'Inicio de sesión exitoso')
                return render(request, 'main/index.html')
            
            messages.error(request, 'Error al iniciar sesión')
    else:
        form = AuthenticationForm()
        return render(request, 'userManagement/user-login.html', {'form': form})
    

#----------------[ User Profile ]----------------
@login_required
def user_profile(request):
    user = request.user

    try:
        avatar = Avatar.objects.get(user=user)
    except Avatar.DoesNotExist:
        avatar = '/media/avatars/default.jpeg'

    return render(request, 'userManagement/user-profile.html', 
                {'user': user, 'avatar': avatar, 'MEDIA_URL': settings.MEDIA_URL})


#----------------[ User Update ]----------------
@login_required
def user_update(request):
    user = request.user

    try:
        avatar = Avatar.objects.get(user=user)
    except Avatar.DoesNotExist:
        avatar = '/media/avatars/default.jpeg'

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado con éxito')
            return redirect('Profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'userManagement/user-update.html', {'form':form, 'avatar':avatar})


#----------------[ Password Update ]----------------

class PasswordUpdate(LoginRequiredMixin, PasswordChangeView):
    template_name = 'userManagement/password-update.html'
    success_url = reverse_lazy('Profile')

#----------------[ Role Assignment ]----------------

def is_superadmin(user):
    return user.role.role == 'master'

@user_passes_test(is_superadmin)
def assing_role(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        role_form = RoleAssignForm(request.POST)
        
        if role_form.is_valid():
            role, created = Role.objects.get_or_create(user=user)
            role.role = role_form.cleaned_data['role']
            role.save()
            return redirect('main/index.html')
    else:    
        role_form = RoleAssignForm()
        
    return render(request, 'assign-role.html', {'form': role_form, 'user':user})




