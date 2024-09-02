from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from userManagement.forms import UserRegisterForm, UserUpdateForm, RoleAssignForm, CustomAuthenticationForm, CustomPasswordChangeForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect
from .models import Role, User, Avatar
import django.contrib.messages as messages
from django.conf import settings
from django.views.generic import ListView, UpdateView


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


#----------------[ Admin User List & Role Assignment ]----------------
def is_superadmin(user):
    try:
        return user.role.role == 'master'
    except Role.DoesNotExist:
        return False

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    context_object_name = 'users'
    template_name = 'userManagement/user-list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(username__icontains=search_query)
        return queryset
    
    def test_func(self):
        return is_superadmin(self.request.user)
    
    def handle_no_permission(self):
        return redirect('index')


class UserDetailUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Role
    form_class = RoleAssignForm
    template_name = 'userManagement/user-detail.html'
    context_object_name = 'user'
    
    def get_object(self, queryset=None):
        user = get_object_or_404(User, id=self.kwargs['pk'])
        role, created = Role.objects.get_or_create(user=user)
        return role
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        context['user'] = user
        return context
    
    def get_success_url(self):
        return reverse_lazy('UserDetail', kwargs={'pk': self.kwargs['pk']})

    def test_func(self):
        return is_superadmin(self.request.user)
    
    def handle_no_permission(self):
        return redirect('index')




