from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Exists, F, OuterRef, Prefetch, Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal, InvalidOperation
from PIL import Image, UnidentifiedImageError
from .models import Annonce, ImageAnnonce, Equipement, AnnonceEquipement, VueAnnonce
from .forms import AnnonceForm


MAX_ANNONCE_IMAGES = 10
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_FORMATS = {'JPEG', 'PNG', 'WEBP'}


def _register_annonce_view(request, annonce):
    """Compte une première visite par compte, ou par session pour les visiteurs anonymes."""
    if request.user.is_authenticated:
        session_seen_ids = {
            str(value) for value in request.session.get('annonces_vues_session', [])
        }
        _, is_new_view = VueAnnonce.objects.get_or_create(annonce=annonce, user=request.user)
        # Si la visite avait déjà été comptée avant la connexion, on mémorise le compte
        # sans incrémenter une seconde fois le compteur.
        if str(annonce.pk) in session_seen_ids:
            is_new_view = False
    else:
        session_key = 'annonces_vues_session'
        seen_ids = [str(value) for value in request.session.get(session_key, [])]
        annonce_id = str(annonce.pk)
        is_new_view = annonce_id not in seen_ids
        if is_new_view:
            request.session[session_key] = (seen_ids + [annonce_id])[-500:]

    if is_new_view:
        Annonce.objects.filter(pk=annonce.pk).update(nombre_vues=F('nombre_vues') + 1)
        annonce.refresh_from_db(fields=['nombre_vues'])


def _validate_uploaded_images(files, total_after_save):
    errors = []
    if total_after_save > MAX_ANNONCE_IMAGES:
        errors.append(f'Une annonce peut contenir au maximum {MAX_ANNONCE_IMAGES} photos.')
    for uploaded in files:
        if uploaded.size > MAX_IMAGE_SIZE:
            errors.append(f'Chaque photo doit peser au maximum 5 Mo : {uploaded.name}.')
            continue
        try:
            with Image.open(uploaded) as image:
                if image.format not in ALLOWED_IMAGE_FORMATS:
                    errors.append(f'Format de photo non accepté pour {uploaded.name}. Utilisez JPEG, PNG ou WebP.')
                else:
                    image.verify()
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
            errors.append(f'Le fichier {uploaded.name} n’est pas une image valide.')
        finally:
            uploaded.seek(0)
    return errors


def index_view(request):
    """Vue de la page d'accueil"""
    def homepage_queryset(**filters):
        queryset = Annonce.objects.filter(statut='active', **filters).prefetch_related(
            Prefetch(
                'images',
                queryset=ImageAnnonce.objects.order_by('-is_principale', 'ordre', 'id'),
                to_attr='homepage_images',
            )
        )
        if request.user.is_authenticated:
            from messagerie.models import Favori
            queryset = queryset.annotate(
                is_favori=Exists(
                    Favori.objects.filter(user=request.user, annonce_id=OuterRef('pk'))
                )
            )
        return queryset.order_by('-created_at')

    annonces_featured = homepage_queryset(is_premium=True)[:6]
    
    annonces_maisons = homepage_queryset(type_bien='maison')[:4]
    
    annonces_meubles = homepage_queryset(is_meuble=True)[:4]
    
    annonces_studios = homepage_queryset(type_bien='studio')[:4]

    annonces_villas = homepage_queryset(type_bien='villa')[:4]
    
    annonces_appartements = homepage_queryset(type_bien='appartement')[:4]
    
    return render(request, 'annonces/index.html', {
        'annonces_featured': annonces_featured,
        'annonces_maisons': annonces_maisons,
        'annonces_meubles': annonces_meubles,
        'annonces_studios': annonces_studios,
        'annonces_villas': annonces_villas,
        'annonces_appartements': annonces_appartements,
        'has_homepage_listings': any((
            annonces_featured,
            annonces_maisons,
            annonces_meubles,
            annonces_studios,
            annonces_villas,
            annonces_appartements,
        )),
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
    
    _register_annonce_view(request, annonce)
    
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
        annonces = annonces.filter(Q(ville__icontains=ville) | Q(quartier__icontains=ville))
    if type_bien:
        annonces = annonces.filter(type_bien=type_bien)
    if prix_min:
        try:
            prix_min_value = Decimal(prix_min)
            if prix_min_value.is_finite() and prix_min_value >= 0:
                annonces = annonces.filter(prix__gte=prix_min_value)
        except InvalidOperation:
            pass
    if prix_max:
        try:
            prix_max_value = Decimal(prix_max)
            if prix_max_value.is_finite() and prix_max_value >= 0:
                annonces = annonces.filter(prix__lte=prix_max_value)
        except InvalidOperation:
            pass
    if chambres:
        try:
            chambres_value = int(chambres)
        except (TypeError, ValueError):
            chambres_value = None
        if chambres_value is not None:
            if chambres_value >= 4:
                annonces = annonces.filter(nombre_chambres__gte=4)
            else:
                annonces = annonces.filter(nombre_chambres=chambres_value)

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
    if request.user.role != 'proprietaire' or not proprietaire:
        messages.error(request, 'Seuls les propriétaires peuvent publier une annonce.')
        return redirect('annonces:index')

    if request.method == 'POST':
        form = AnnonceForm(request.POST)
        images = request.FILES.getlist('images')
        image_errors = _validate_uploaded_images(images, len(images))
        form_valid = form.is_valid()
        if form_valid and not image_errors:
            equipment_ids = {
                int(value) for value in request.POST.getlist('equipements') if value.isdigit()
            }
            saved_image_names = []
            try:
                with transaction.atomic():
                    annonce = form.save(commit=False)
                    annonce.proprietaire = proprietaire
                    annonce.statut = 'en_attente'
                    # Le statut Premium est réservé à la validation administrative.
                    annonce.is_premium = False
                    annonce.save()

                    for index, image_file in enumerate(images):
                        image = ImageAnnonce.objects.create(
                            annonce=annonce,
                            image=image_file,
                            is_principale=(index == 0),
                            ordre=index,
                        )
                        saved_image_names.append(image.image.name)

                    for equipement in Equipement.objects.filter(pk__in=equipment_ids):
                        AnnonceEquipement.objects.get_or_create(
                            annonce=annonce,
                            equipement=equipement,
                            defaults={'description': ''},
                        )
            except Exception:
                storage = ImageAnnonce._meta.get_field('image').storage
                for file_name in saved_image_names:
                    storage.delete(file_name)
                raise
            messages.success(request, 'Votre annonce a été créée et est en attente de validation.')
            return redirect('accounts:profil_proprietaire')
    else:
        form = AnnonceForm()

    equipements = Equipement.objects.all().order_by('nom')
    return render(request, 'annonces/annonce_form.html', {
        'form': form,
        'equipements': equipements,
        'selected_equipement_ids': {
            int(value) for value in request.POST.getlist('equipements') if value.isdigit()
        } if request.method == 'POST' else set(),
        'upload_errors': image_errors if request.method == 'POST' else [],
        'max_announcement_images': MAX_ANNONCE_IMAGES,
        'is_edit': False,
    })


@login_required
def annonce_edit_view(request, pk):
    """Modifier une annonce appartenant au propriétaire connecté."""
    proprietaire = getattr(request.user, 'proprietaire', None)
    if request.user.role != 'proprietaire' or not proprietaire:
        messages.error(request, 'Seuls les propriétaires peuvent modifier une annonce.')
        return redirect('annonces:index')

    annonce = get_object_or_404(Annonce, pk=pk, proprietaire=proprietaire)
    existing_images = list(annonce.images.all())
    upload_errors = []
    if request.method == 'POST':
        form = AnnonceForm(request.POST, instance=annonce)
        new_images = request.FILES.getlist('images')
        existing_ids = {image.pk for image in existing_images}
        raw_remove_ids = request.POST.getlist('remove_images')
        remove_ids = {int(value) for value in raw_remove_ids if value.isdigit()}
        if any(not value.isdigit() for value in raw_remove_ids) or not remove_ids.issubset(existing_ids):
            upload_errors.append('La sélection des photos à supprimer est invalide.')
        remaining_images = [image for image in existing_images if image.pk not in remove_ids]
        upload_errors.extend(
            _validate_uploaded_images(new_images, len(remaining_images) + len(new_images))
        )

        image_orders = {}
        for image in remaining_images:
            try:
                order = int(request.POST.get(f'image_order_{image.pk}', image.ordre))
                if order < 0:
                    raise ValueError
                image_orders[image.pk] = order
            except (TypeError, ValueError):
                upload_errors.append('L’ordre des photos doit être un nombre positif ou nul.')
        form_valid = form.is_valid()
        if form_valid and not upload_errors:
            equipment_ids = {
                int(value) for value in request.POST.getlist('equipements') if value.isdigit()
            }
            selected_primary = request.POST.get('image_main', '')
            selected_primary_id = int(selected_primary) if selected_primary.isdigit() else None
            if selected_primary_id not in {image.pk for image in remaining_images}:
                selected_primary_id = None
            new_images_primary = request.POST.get('new_images_primary') == 'on' and bool(new_images)
            if selected_primary_id is None and not new_images_primary and remaining_images:
                selected_primary_id = min(remaining_images, key=lambda image: image_orders[image.pk]).pk

            removed_files = [image.image.name for image in existing_images if image.pk in remove_ids]
            uploaded_file_names = []
            try:
                with transaction.atomic():
                    annonce = form.save(commit=False)
                    annonce.statut = 'en_attente'
                    annonce.save()

                    for image in existing_images:
                        if image.pk in remove_ids:
                            image.delete()
                            continue
                        image.ordre = image_orders[image.pk]
                        image.is_principale = image.pk == selected_primary_id
                        image.save(update_fields=['ordre', 'is_principale'])

                    if new_images_primary and remaining_images:
                        ImageAnnonce.objects.filter(annonce=annonce).update(is_principale=False)

                    next_order = max(image_orders.values(), default=-1) + 1
                    for index, image_file in enumerate(new_images):
                        image = ImageAnnonce.objects.create(
                            annonce=annonce,
                            image=image_file,
                            is_principale=(
                                (new_images_primary and index == 0)
                                or (not remaining_images and index == 0)
                            ),
                            ordre=(0 if new_images_primary and index == 0 else next_order + index),
                        )
                        uploaded_file_names.append(image.image.name)

                    AnnonceEquipement.objects.filter(annonce=annonce).exclude(
                        equipement_id__in=equipment_ids
                    ).delete()
                    for equipement in Equipement.objects.filter(pk__in=equipment_ids):
                        AnnonceEquipement.objects.get_or_create(
                            annonce=annonce,
                            equipement=equipement,
                            defaults={'description': ''},
                        )
            except Exception:
                for file_name in uploaded_file_names:
                    ImageAnnonce._meta.get_field('image').storage.delete(file_name)
                raise

            storage = ImageAnnonce._meta.get_field('image').storage
            for file_name in removed_files:
                storage.delete(file_name)
            messages.success(request, 'Annonce mise à jour et envoyée en validation.')
            return redirect('accounts:profil_proprietaire')
    else:
        form = AnnonceForm(instance=annonce)

    equipements = Equipement.objects.all().order_by('nom')
    if request.method == 'POST':
        selected_equipement_ids = {
            int(value) for value in request.POST.getlist('equipements') if value.isdigit()
        }
    else:
        selected_equipement_ids = set(
            annonce.equipements.values_list('equipement_id', flat=True)
        )
    removed_image_ids = {
        int(value) for value in request.POST.getlist('remove_images') if value.isdigit()
    } if request.method == 'POST' else set()
    remaining_image_ids = {image.pk for image in existing_images} - removed_image_ids
    requested_primary_id = (
        int(request.POST.get('image_main'))
        if request.method == 'POST' and request.POST.get('image_main', '').isdigit()
        else None
    )
    selected_primary_id = requested_primary_id if requested_primary_id in remaining_image_ids else None
    if selected_primary_id is None:
        selected_primary_id = next(
            (image.pk for image in existing_images if image.pk in remaining_image_ids and image.is_principale),
            next((image.pk for image in existing_images if image.pk in remaining_image_ids), None),
        )
    return render(request, 'annonces/annonce_form.html', {
        'form': form,
        'equipements': equipements,
        'selected_equipement_ids': selected_equipement_ids,
        'annonce': annonce,
        'is_edit': True,
        'upload_errors': upload_errors,
        'max_announcement_images': MAX_ANNONCE_IMAGES,
        'selected_primary_id': selected_primary_id,
        'new_images_primary_selected': request.method == 'POST' and request.POST.get('new_images_primary') == 'on',
        'removed_image_ids': removed_image_ids,
        'existing_image_rows': [
            {
                'image': image,
                'submitted_order': request.POST.get(f'image_order_{image.pk}', image.ordre)
                if request.method == 'POST' else image.ordre,
            }
            for image in existing_images
        ],
    })
