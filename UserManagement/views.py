from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from userManagement.forms import UserRegisterForm, UserUpdateForm, RoleAssignForm, CustomAuthenticationForm, CustomPasswordChangeForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect
from .models import Role, User, Avatar
import django.contrib.messages as messages
from django.conf import settings
from django.views.generic import ListView, DetailView, UpdateView


#----------------[ User Register ]----------------
def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado con éxito')
            return redirect('index')
        else:
            messages.error(request, 'Error de formulario')
    else:
        form = UserRegisterForm()
    
    return render(request, 'userManagement/user-register.html', {'form': form})


#----------------[ User Login ]----------------
def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                messages.success(request, 'Inicio de sesión exitoso')
                return redirect('index')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = CustomAuthenticationForm()
    
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

class PasswordUpdate (LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'userManagement/password-update.html'
    success_url = reverse_lazy('Profile')

    def form_invalid(self, form):
        return super().form_invalid(form)


#----------------[ Role Assignment ]----------------

class UserListView(LoginRequiredMixin, ListView):
    model = User
    context_object_name = 'users'
    template_name = 'userManagement/user-list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(username__icontains=search_query)
        return queryset


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'userManagement/user-detail.html'


class UserRoleUpdateView(LoginRequiredMixin, UpdateView):
    model = Role
    fields = ['role']
    template_name = 'userManagement/user-detail.html'
    
    def get_object(self):
        user = get_object_or_404(User, id=self.kwargs['pk'])
        role, created = Role.objects.get_or_create(user=user)
        return role
    
    def form_valid(self, form):
        role = form.save(commit=False)
        role.user = get_object_or_404(User, id=self.kwargs['pk'])
        role.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('Users')



def is_superadmin(user):
    try:
        return user.role.role == 'master'
    except Role.DoesNotExist:
        return False

""" @user_passes_test(is_superadmin)
def user_list(request):
    search_query = request.GET.get('search', '')
    user_list = User.objects.filter(username__icontains=search_query)
    return render(request, 'user-list.html', {'users': user_list, 'search_query': search_query})

@user_passes_test(is_superadmin)
def assing_role(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        role_form = RoleAssignForm(request.POST)
        
        if role_form.is_valid():
            role, created = Role.objects.get_or_create(user=user)
            role.role = role_form.cleaned_data['role']
            role.save()
            return redirect('Users')
    else:    
        role_form = RoleAssignForm()
        try:
            role = Role.objects.get(user=user)
            role_form.initial['role'] = role.role
        except Role.DoesNotExist:
            pass
        
    return render(request, 'assign-role.html', {'form': role_form, 'user':user})


 """

