from django.urls import path
from django.contrib.auth.views import LogoutView
from userManagement import views

urlpatterns = [
    path('login/', views.user_login, name='Login'),
    path('register/', views.user_register, name='Register'),
    path('logout/', LogoutView.as_view(template_name='main/index'), name='Logout'),
    path('profile/', views.user_profile, name="Profile"),
    path('update/', views.user_update, name='Update'),
    path('password-update/', views.PasswordUpdate.as_view(), name='PasswordUpdate'),    
    path('users/', views.UserListView.as_view(), name='Users'),
    path('user/<int:pk>', views.UserDetailUpdateView.as_view(), name='UserDetail'),
]
