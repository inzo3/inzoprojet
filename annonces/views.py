from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Annonce, ImageAnnonce, Equipement, AnnonceEquipement
from .forms import AnnonceForm


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
    annonce = get_object_or_404(Annonce, pk=pk)

    # Annonces en attente/désactivées : visible uniquement par le propriétaire
    if annonce.statut != 'active':
        from django.http import Http404
        proprietaire = getattr(request.user, 'proprietaire', None)
        if not (request.user.is_authenticated and proprietaire and annonce.proprietaire_id == proprietaire.pk):
            raise Http404("Annonce non disponible")
    
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

    # Vérifier si le contact est débloqué pour cet utilisateur (photo et infos visibles)
    from django.utils import timezone
    from paiements.models import ContactDebloque
    contact_debloque = False
    contact_debloque_expiration = None
    if request.user.is_authenticated:
        cd = ContactDebloque.objects.filter(
            user=request.user,
            annonce=annonce,
            est_actif=True,
            date_expiration__gt=timezone.now(),
        ).first()
        if cd:
            contact_debloque = True
            contact_debloque_expiration = cd.date_expiration
    # Le propriétaire voit toujours son propre contact en clair (pas de décompte)
    if not contact_debloque and request.user.is_authenticated:
        proprietaire = getattr(request.user, 'proprietaire', None)
        if proprietaire and annonce.proprietaire_id == proprietaire.pk:
            contact_debloque = True

    return render(request, 'annonces/annonce_detail.html', {
        'annonce': annonce,
        'images': images,
        'equipements': equipements,
        'annonces_similaires': annonces_similaires,
        'is_favori': is_favori,
        'contact_debloque': contact_debloque,
        'contact_debloque_expiration': contact_debloque_expiration,
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


@login_required
def annonce_create_view(request):
    """Vue pour publier une nouvelle annonce (réservée aux propriétaires)."""
    proprietaire = getattr(request.user, 'proprietaire', None)
    if not proprietaire:
        messages.error(request, 'Seuls les propriétaires peuvent publier une annonce.')
        return redirect('annonces:index')

    if request.method == 'POST':
        form = AnnonceForm(request.POST)
        if form.is_valid():
            annonce = form.save(commit=False)
            annonce.proprietaire = proprietaire
            annonce.statut = 'en_attente'
            annonce.save()

            # Images
            images = request.FILES.getlist('images')
            for i, img in enumerate(images):
                if img:
                    ImageAnnonce.objects.create(
                        annonce=annonce,
                        image=img,
                        is_principale=(i == 0),
                        ordre=i,
                    )

            # Équipements
            equipement_ids = request.POST.getlist('equipements')
            for eq_id in equipement_ids:
                if eq_id:
                    try:
                        equipement = Equipement.objects.get(pk=eq_id)
                        AnnonceEquipement.objects.get_or_create(
                            annonce=annonce,
                            equipement=equipement,
                            defaults={'description': ''},
                        )
                    except Equipement.DoesNotExist:
                        pass

            messages.success(request, 'Votre annonce a été créée et est en attente de validation.')
            return redirect('accounts:profil_proprietaire')
    else:
        form = AnnonceForm()

    equipements = Equipement.objects.all().order_by('nom')
    return render(request, 'annonces/annonce_form.html', {
        'form': form,
        'equipements': equipements,
        'is_edit': False,
    })
