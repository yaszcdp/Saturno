from django.contrib import admin
from .models import Role, Avatar

# Register your models here.
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'role')

admin.site.register(Avatar)