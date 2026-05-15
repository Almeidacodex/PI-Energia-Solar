from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('email_mascarado','date_joined','is_active')
    search_fields = ('email',)
    ordering = ('date_joined',)

    # Remove o campo username da tela de edição
    fieldsets = (
        (None,       {'fields': ('email','password')}),
        ('Permissões', {'fields': ('is_active','is_staff','is_superuser')}),
        ('Datas',    {'fields': ( 'last_login', 'date_joined')}),

    )
    add_fieldsets = (
        (None, {
            'fields': ('email','password1','password2')
        })
    )