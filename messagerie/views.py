from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from annonces.models import Annonce
from .models import Message, Favori


@login_required
def ajouter_favori(request, annonce_id):
    """Ajouter une annonce aux favoris"""
    annonce = get_object_or_404(Annonce, pk=annonce_id)
    favori, created = Favori.objects.get_or_create(
        user=request.user,
        annonce=annonce
    )
    if created:
        messages.success(request, 'Annonce ajoutée aux favoris!')
    else:
        messages.info(request, 'Cette annonce est déjà dans vos favoris.')
    return redirect('annonces:annonce_detail', pk=annonce_id)


@login_required
def retirer_favori(request, annonce_id):
    """Retirer une annonce des favoris"""
    annonce = get_object_or_404(Annonce, pk=annonce_id)
    Favori.objects.filter(user=request.user, annonce=annonce).delete()
    messages.success(request, 'Annonce retirée des favoris.')
    return redirect('annonces:annonce_detail', pk=annonce_id)


@login_required
def envoyer_message(request, annonce_id):
    """Envoyer un message au propriétaire"""
    annonce = get_object_or_404(Annonce, pk=annonce_id)
    
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        sujet = request.POST.get('sujet', f'Demande pour {annonce.titre}')
        
        Message.objects.create(
            expediteur=request.user,
            destinataire=annonce.proprietaire.user,
            annonce=annonce,
            sujet=sujet,
            contenu=contenu
        )
        
        messages.success(request, 'Message envoyé avec succès!')
        return redirect('annonces:annonce_detail', pk=annonce_id)
    
    return render(request, 'messagerie/envoyer_message.html', {
        'annonce': annonce
    })
