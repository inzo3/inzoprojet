from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth import login, authenticate # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib import messages # type: ignore
from .models import User, Proprietaire, Locataire


def login_view(request):
    """Vue de connexion"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Connexion réussie!')
            if user.role == 'proprietaire':
                return redirect('accounts:profil_proprietaire')
            elif user.role == 'locataire':
                return redirect('accounts:profil_locataire')
            return redirect('annonces:index')
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
    return render(request, 'accounts/login.html')


def register_view(request):
    """Vue d'inscription"""
    if request.method == 'POST':
        role = request.POST.get('register-role')
        first_name = request.POST.get('register-firstname')
        last_name = request.POST.get('register-lastname')
        email = request.POST.get('register-email')
        password = request.POST.get('register-password')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
            return render(request, 'accounts/register.html')
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        # Créer le profil selon le rôle
        if role == 'proprietaire':
            Proprietaire.objects.create(user=user)
        elif role == 'locataire':
            Locataire.objects.create(user=user)
        
        login(request, user)
        messages.success(request, 'Inscription réussie!')
        if role == 'proprietaire':
            return redirect('accounts:profil_proprietaire')
        elif role == 'locataire':
            return redirect('accounts:profil_locataire')
        return redirect('annonces:index')
    
    return render(request, 'accounts/register.html')


@login_required
def profil_locataire_view(request):
    """Vue du profil locataire"""
    locataire = getattr(request.user, 'locataire', None)
    return render(request, 'accounts/profil_locataire.html', {
        'locataire': locataire
    })


@login_required
def profil_proprietaire_view(request):
    """Vue du profil propriétaire"""
    proprietaire = getattr(request.user, 'proprietaire', None)
    annonces_actives = 0
    total_vues = 0
    if proprietaire:
        annonces_actives = proprietaire.annonces.filter(statut='active').count()
        total_vues = sum(annonce.nombre_vues for annonce in proprietaire.annonces.all())
    return render(request, 'accounts/profil_proprietaire.html', {
        'proprietaire': proprietaire,
        'annonces_actives': annonces_actives,
        'total_vues': total_vues,
    })
