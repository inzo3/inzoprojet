from django.contrib import admin
from .models import Paiement, ContactDebloque


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['user', 'annonce', 'montant', 'methode', 'statut', 'date_paiement']
    list_filter = ['statut', 'methode', 'date_paiement']
    search_fields = ['user__username', 'user__email', 'transaction_id']


@admin.register(ContactDebloque)
class ContactDebloqueAdmin(admin.ModelAdmin):
    list_display = ['user', 'annonce', 'date_deblocage', 'date_expiration', 'est_actif']
    list_filter = ['est_actif', 'date_deblocage']
