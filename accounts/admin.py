from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Proprietaire, Locataire


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_verified', 'is_active']
    list_filter = ['role', 'is_verified', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('role', 'phone', 'avatar', 'is_verified')}),
    )


@admin.register(Proprietaire)
class ProprietaireAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'total_avis', 'is_premium']
    list_filter = ['is_premium']


@admin.register(Locataire)
class LocataireAdmin(admin.ModelAdmin):
    list_display = ['user', 'ville_preferee', 'quartier_prefere']
