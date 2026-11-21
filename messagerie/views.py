from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.http import url_has_allowed_host_and_scheme
from annonces.models import Annonce
from .models import Message, Favori
from .forms import MessageForm


@login_required
def messages_recus(request):
    """Boîte de réception paginée du propriétaire connecté."""
    if request.user.role != 'proprietaire':
        messages.error(request, 'Cette boîte de réception est réservée aux propriétaires.')
        return redirect('accounts:profil_locataire')
    inbox = Message.objects.filter(destinataire=request.user).select_related(
        'expediteur', 'annonce'
    ).order_by('-date_envoi', '-pk')
    paginator = Paginator(inbox, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'messagerie/messages_recus.html', {
        'page_obj': page,
        'unread_count': inbox.filter(lu=False).count(),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def detail_message(request, pk):
    message = get_object_or_404(
        Message.objects.select_related('expediteur', 'destinataire', 'annonce', 'reponse_a'),
        pk=pk,
    )
    root = message.reponse_a or message
    participants = {root.expediteur_id, root.destinataire_id}
    if request.user.pk not in participants:
        from django.http import Http404
        raise Http404

    if message.destinataire_id == request.user.pk and not message.lu:
        message.lu = True
        message.save(update_fields=['lu'])

    thread = Message.objects.filter(Q(pk=root.pk) | Q(reponse_a=root)).select_related(
        'expediteur', 'destinataire'
    ).order_by('date_envoi', 'pk')
    other_user_id = root.destinataire_id if request.user.pk == root.expediteur_id else root.expediteur_id
    form = MessageForm(request.POST or None, initial={'sujet': root.sujet})
    if request.method == 'POST' and form.is_valid():
        reply = form.save(commit=False)
        reply.expediteur = request.user
        reply.destinataire_id = other_user_id
        reply.annonce = root.annonce
        reply.reponse_a = root
        reply.save()
        messages.success(request, 'Votre réponse a été envoyée.')
        return redirect('messagerie:detail_message', pk=root.pk)

    return render(request, 'messagerie/detail_message.html', {
        'message': root,
        'thread': thread,
        'form': form,
        'other_user': root.destinataire if request.user.pk == root.expediteur_id else root.expediteur,
    })


@login_required
@require_POST
def supprimer_conversation(request, pk):
    message = get_object_or_404(Message.objects.select_related('reponse_a'), pk=pk)
    root = message.reponse_a or message
    if request.user.pk not in {root.expediteur_id, root.destinataire_id}:
        from django.http import Http404
        raise Http404
    Message.objects.filter(Q(pk=root.pk) | Q(reponse_a=root)).delete()
    messages.success(request, 'La conversation a été supprimée.')
    if request.user.role == 'proprietaire':
        return redirect('messagerie:messages_recus')
    return redirect('accounts:profil_locataire')


def _favori_redirect(request, annonce_id):
    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect('annonces:annonce_detail', pk=annonce_id)


@login_required
@require_POST
def ajouter_favori(request, annonce_id):
    """Ajouter une annonce aux favoris"""
    annonce = get_object_or_404(Annonce, pk=annonce_id)
    favori, created = Favori.objects.get_or_create(
        user=request.user,
        annonce=annonce
    )
    if created:
        messages.success(request, 'Annonce ajoutée aux favoris!')
    return _favori_redirect(request, annonce_id)


@login_required
@require_POST
def retirer_favori(request, annonce_id):
    """Retirer une annonce des favoris"""
    annonce = get_object_or_404(Annonce, pk=annonce_id)
    Favori.objects.filter(user=request.user, annonce=annonce).delete()
    messages.success(request, 'Annonce retirée des favoris.')
    return _favori_redirect(request, annonce_id)


@login_required
@require_http_methods(['GET', 'POST'])
def envoyer_message(request, annonce_id):
    """Envoyer un message au propriétaire"""
    annonce = Annonce.objects.filter(pk=annonce_id).select_related(
        'proprietaire__user'
    ).first()
    if annonce is None:
        messages.error(request, 'Cette annonce n’existe plus ou a été supprimée.')
        return redirect('annonces:recherche')
    if annonce.statut != 'active':
        messages.info(request, 'Cette annonce n’est pas publiée actuellement ; vous ne pouvez pas la contacter.')
        proprietaire = getattr(request.user, 'proprietaire', None)
        if proprietaire and annonce.proprietaire_id == proprietaire.pk:
            return redirect('annonces:annonce_detail', pk=annonce.pk)
        return redirect('annonces:recherche')
    if annonce.proprietaire.user_id == request.user.pk:
        messages.info(request, 'Vous ne pouvez pas envoyer un message à propos de votre propre annonce.')
        return redirect('annonces:annonce_detail', pk=annonce_id)

    form = MessageForm(request.POST or None, initial={
        'sujet': f'Demande pour {annonce.titre}',
    })
    if request.method == 'POST' and form.is_valid():
        message = form.save(commit=False)
        message.expediteur = request.user
        message.destinataire = annonce.proprietaire.user
        message.annonce = annonce
        message.save()
        messages.success(request, 'Message envoyé avec succès!')
        return redirect('annonces:annonce_detail', pk=annonce_id)
    
    return render(request, 'messagerie/envoyer_message.html', {
        'annonce': annonce,
        'form': form,
    })
