from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Annonce, ImageAnnonce


def index_view(request):
    """Vue de la page d'accueil"""
    annonces_featured = Annonce.objects.filter(
        is_premium=True, 
        statut='active'
    ).order_by('-created_at')[:6]
    
    annonces_maisons = Annonce.objects.filter(
        type_bien='maison',
        statut='active'
    ).order_by('-created_at')[:4]
    
    annonces_meubles = Annonce.objects.filter(
        is_meuble=True,
        statut='active'
    ).order_by('-created_at')[:4]
    
    annonces_studios = Annonce.objects.filter(
        type_bien='studio',
        statut='active'
    ).order_by('-created_at')[:4]
    
    annonces_appartements = Annonce.objects.filter(
        type_bien='appartement',
        statut='active'
    ).order_by('-created_at')[:4]
    
    return render(request, 'annonces/index.html', {
        'annonces_featured': annonces_featured,
        'annonces_maisons': annonces_maisons,
        'annonces_meubles': annonces_meubles,
        'annonces_studios': annonces_studios,
        'annonces_appartements': annonces_appartements,
    })


def annonce_detail_view(request, pk):
    """Vue de détail d'une annonce"""
    annonce = get_object_or_404(Annonce, pk=pk, statut='active')
    
    # Incrémenter le nombre de vues
    annonce.nombre_vues += 1
    annonce.save(update_fields=['nombre_vues'])
    
    images = annonce.images.all()
    equipements = annonce.equipements.all()
    
    # Annonces similaires
    annonces_similaires = Annonce.objects.filter(
        type_bien=annonce.type_bien,
        ville=annonce.ville,
        statut='active'
    ).exclude(pk=annonce.pk)[:2]
    
    # Vérifier si l'utilisateur a déjà cette annonce en favoris
    is_favori = False
    if request.user.is_authenticated:
        from messagerie.models import Favori
        is_favori = Favori.objects.filter(user=request.user, annonce=annonce).exists()
    
    return render(request, 'annonces/annonce_detail.html', {
        'annonce': annonce,
        'images': images,
        'equipements': equipements,
        'annonces_similaires': annonces_similaires,
        'is_favori': is_favori,
    })


def recherche_view(request):
    """Vue de recherche d'annonces"""
    query = request.GET.get('q', '')
    ville = request.GET.get('ville', '')
    type_bien = request.GET.get('type', '')
    prix_min = request.GET.get('prix_min', '')
    prix_max = request.GET.get('prix_max', '')
    chambres = request.GET.get('chambres', '')
    
    annonces = Annonce.objects.filter(statut='active')
    
    if ville:
        annonces = annonces.filter(ville__icontains=ville)
    if type_bien:
        annonces = annonces.filter(type_bien=type_bien)
    if prix_min:
        annonces = annonces.filter(prix__gte=prix_min)
    if prix_max:
        annonces = annonces.filter(prix__lte=prix_max)
    if chambres:
        annonces = annonces.filter(nombre_chambres=chambres)
    if query:
        annonces = annonces.filter(
            Q(titre__icontains=query) | 
            Q(description__icontains=query) |
            Q(quartier__icontains=query)
        )
    
    return render(request, 'annonces/recherche.html', {
        'annonces': annonces,
        'query': query,
        'ville': ville,
        'type_bien': type_bien,
    })
