from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from annonces.models import Annonce
from .models import Paiement, ContactDebloque


@login_required
def paiement_view(request, annonce_id):
    """Vue pour le paiement d'un contact"""
    from annonces.models import Annonce
    annonce = get_object_or_404(Annonce, pk=annonce_id, statut='active')
    
    # Vérifier si le contact est déjà débloqué
    contact_debloque = ContactDebloque.objects.filter(
        user=request.user,
        annonce=annonce,
        est_actif=True,
        date_expiration__gt=timezone.now()
    ).first()
    
    if contact_debloque:
        messages.info(request, 'Vous avez déjà débloqué ce contact.')
        return redirect('annonces:annonce_detail', pk=annonce_id)
    
    if request.method == 'POST':
        methode = request.POST.get('paymentMethod')
        numero_telephone = request.POST.get('phonePayment')
        montant = 1000  # Montant fixe pour débloquer un contact
        
        # Créer le paiement
        paiement = Paiement.objects.create(
            user=request.user,
            annonce=annonce,
            montant=montant,
            methode=methode,
            numero_telephone=numero_telephone,
            statut='valide'  # En production, vérifier avec l'API de paiement
        )
        
        # Créer le contact débloqué (valable 24 heures)
        ContactDebloque.objects.create(
            user=request.user,
            annonce=annonce,
            paiement=paiement,
            date_expiration=timezone.now() + timedelta(hours=24)
        )
        
        messages.success(request, 'Contact débloqué avec succès! Visible pendant 24 heures.')
        return redirect('annonces:annonce_detail', pk=annonce_id)
    
    return render(request, 'paiements/paiement.html', {
        'annonce': annonce
    })
