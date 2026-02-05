from django.contrib import admin
from .models import Message, Favori


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['expediteur', 'destinataire', 'annonce', 'lu', 'date_envoi']
    list_filter = ['lu', 'date_envoi']
    search_fields = ['expediteur__username', 'destinataire__username', 'contenu']


@admin.register(Favori)
class FavoriAdmin(admin.ModelAdmin):
    list_display = ['user', 'annonce', 'date_ajout']
    list_filter = ['date_ajout']
