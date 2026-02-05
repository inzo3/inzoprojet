from django.contrib import admin
from .models import Annonce, ImageAnnonce, Equipement, AnnonceEquipement


class ImageAnnonceInline(admin.TabularInline):
    model = ImageAnnonce
    extra = 1


class AnnonceEquipementInline(admin.TabularInline):
    model = AnnonceEquipement
    extra = 1


@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ['titre', 'proprietaire', 'ville', 'prix', 'statut', 'is_premium']
    list_filter = ['type_bien', 'statut', 'is_premium', 'is_meuble', 'ville']
    search_fields = ['titre', 'description', 'ville', 'quartier']
    inlines = [ImageAnnonceInline, AnnonceEquipementInline]


@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'icone']


@admin.register(ImageAnnonce)
class ImageAnnonceAdmin(admin.ModelAdmin):
    list_display = ['annonce', 'is_principale', 'ordre']
