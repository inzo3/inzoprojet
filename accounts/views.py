from django.shortcuts import render, redirect  # type: ignore
from django.contrib.auth import login, authenticate, logout  # type: ignore
from django.contrib.auth.decorators import login_required  # type: ignore
from django.contrib import messages  # type: ignore
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError, transaction
from django.db.models import Prefetch, Sum
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from smtplib import SMTPException
import hashlib
from .models import User, Proprietaire, Locataire
from .forms import ProfileForm, LocatairePreferencesForm, ProprietairePreferencesForm
from annonces.models import Annonce, ImageAnnonce


LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60


def _login_throttle_key(request, email):
    # Hash identifiers so cache keys do not expose submitted email addresses.
    remote_addr = request.META.get('REMOTE_ADDR', '')
    identity = f'{remote_addr}:{(email or "").strip().casefold()}'
    return 'login-failures:' + hashlib.sha256(identity.encode()).hexdigest()


def _send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verification_url = request.build_absolute_uri(
        reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
    )
    email_context = {'user': user, 'verification_url': verification_url}
    send_mail(
        subject='Confirmez votre adresse e-mail — LocaHome',
        message=render_to_string('registration/email_verification.txt', email_context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=render_to_string('registration/email_verification.html', email_context),
        fail_silently=False,
    )


def login_view(request):
    """Vue de connexion"""
    next_url = request.POST.get('next') or request.GET.get('next', '')
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''
        throttle_key = _login_throttle_key(request, email)
        if cache.get(throttle_key, 0) >= LOGIN_MAX_ATTEMPTS:
            messages.error(request, 'Trop de tentatives. Réessayez dans 15 minutes.')
            return render(request, 'accounts/login.html', {'next_url': next_url}, status=429)

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            cache.delete(throttle_key)
            messages.success(request, 'Connexion réussie!')
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                return redirect(next_url)
            if user.role == 'proprietaire':
                return redirect('accounts:profil_proprietaire')
            elif user.role == 'locataire':
                return redirect('accounts:profil_locataire')
            return redirect('accounts:google_profile')
        else:
            try:
                failures = cache.get(throttle_key, 0)
                if failures == 0:
                    cache.add(throttle_key, 1, LOGIN_LOCKOUT_SECONDS)
                else:
                    cache.incr(throttle_key)
            except ValueError:
                cache.set(throttle_key, 1, LOGIN_LOCKOUT_SECONDS)
            messages.error(request, 'Email ou mot de passe incorrect.')
    return render(request, 'accounts/login.html', {'next_url': next_url})


def register_view(request):
    """Vue d'inscription"""
    if request.method == 'POST':
        role = request.POST.get('register-role')
        first_name = (request.POST.get('register-firstname') or '').strip()
        last_name = (request.POST.get('register-lastname') or '').strip()
        email = (request.POST.get('register-email') or '').strip().casefold()
        password = request.POST.get('register-password') or ''
        password_confirm = request.POST.get('register-password-confirm') or ''
        form_data = {
            'role': role,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
        }
        errors = []

        if role not in {'proprietaire', 'locataire'}:
            errors.append('Sélectionnez un type de compte valide.')
        if not first_name or not last_name:
            errors.append('Saisissez votre prénom et votre nom.')
        if len(first_name) > 150 or len(last_name) > 150:
            errors.append('Le prénom et le nom ne peuvent pas dépasser 150 caractères.')
        try:
            validate_email(email)
        except ValidationError:
            errors.append('Saisissez une adresse e-mail valide.')
        if email and User.objects.filter(email__iexact=email).exists():
            errors.append('Cette adresse e-mail est déjà utilisée.')
        if password != password_confirm:
            errors.append('Les deux mots de passe ne correspondent pas.')

        candidate = User(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        try:
            validate_password(password, user=candidate)
        except ValidationError as exc:
            errors.extend(exc.messages)

        if errors:
            return render(
                request,
                'accounts/register.html',
                {'form_data': form_data, 'form_errors': errors},
                status=400,
            )

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    is_active=False,
                )
                if role == 'proprietaire':
                    Proprietaire.objects.create(user=user)
                else:
                    Locataire.objects.create(user=user)
                _send_verification_email(request, user)
        except (SMTPException, OSError):
            return render(
                request,
                'accounts/register.html',
                {
                    'form_data': form_data,
                    'form_errors': [
                        'Nous ne pouvons pas envoyer l’e-mail de confirmation pour le moment. Réessayez plus tard.'
                    ],
                },
                status=503,
            )
        except IntegrityError:
            return render(
                request,
                'accounts/register.html',
                {
                    'form_data': form_data,
                    'form_errors': ['Cette adresse e-mail est déjà utilisée.'],
                },
                status=400,
            )
        
        return redirect('accounts:verification_sent')
    
    return render(request, 'accounts/register.html')


def verification_sent_view(request):
    """Indiquer à l'utilisateur qu'un lien de confirmation a été envoyé."""
    return render(request, 'registration/email_verification_sent.html')


@require_http_methods(['GET', 'POST'])
def resend_verification_view(request):
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().casefold()
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Saisissez une adresse e-mail valide.')
            return render(request, 'registration/email_verification_resend.html', status=400)

        # Toujours répondre de la même manière afin de ne pas révéler l'existence d'un compte.
        user = User.objects.filter(email__iexact=email, is_active=False).first()
        if user:
            try:
                _send_verification_email(request, user)
            except (SMTPException, OSError):
                messages.error(request, 'L’envoi a échoué. Réessayez dans quelques instants.')
                return render(request, 'registration/email_verification_resend.html', status=503)
        return redirect('accounts:verification_sent')

    return render(request, 'registration/email_verification_resend.html')


@require_http_methods(['GET', 'POST'])
def verify_email_view(request, uidb64, token):
    """Activer un compte uniquement après confirmation depuis sa boîte e-mail."""
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id, is_active=False)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    valid_token = user is not None and default_token_generator.check_token(user, token)
    if request.method == 'POST' and valid_token:
        user.is_active = True
        user.is_verified = True
        user.save(update_fields=['is_active', 'is_verified'])
        messages.success(request, 'Adresse e-mail confirmée. Vous pouvez maintenant vous connecter.')
        return redirect('accounts:login')

    return render(
        request,
        'registration/email_verification_confirm.html',
        {'valid_token': valid_token},
        status=200 if valid_token else 400,
    )


@login_required
@require_http_methods(['GET', 'POST'])
def google_profile_view(request):
    """Compléter le rôle d'un compte créé par connexion sociale."""
    if request.user.role in {'locataire', 'proprietaire'}:
        if request.user.role == 'proprietaire':
            return redirect('accounts:profil_proprietaire')
        return redirect('accounts:profil_locataire')

    if request.method == 'POST':
        role = request.POST.get('role')
        if role not in {'locataire', 'proprietaire'}:
            messages.error(request, 'Sélectionnez un type de compte valide.')
        else:
            with transaction.atomic():
                request.user.role = role
                request.user.save(update_fields=['role'])
                if role == 'proprietaire':
                    Proprietaire.objects.get_or_create(user=request.user)
                else:
                    Locataire.objects.get_or_create(user=request.user)
            messages.success(request, 'Votre profil est prêt.')
            return redirect(
                'accounts:profil_proprietaire'
                if role == 'proprietaire'
                else 'accounts:profil_locataire'
            )

    return render(request, 'accounts/google_profile.html')


@login_required
def profil_locataire_view(request):
    """Vue du profil locataire"""
    if request.user.role != 'locataire':
        return redirect(
            'accounts:profil_proprietaire'
            if request.user.role == 'proprietaire'
            else 'accounts:google_profile'
        )
    locataire, _ = Locataire.objects.get_or_create(user=request.user)
    from messagerie.models import Favori, Message
    from paiements.models import ContactDebloque
    favoris = Favori.objects.filter(user=request.user).select_related('annonce').prefetch_related(
        Prefetch(
            'annonce__images',
            queryset=ImageAnnonce.objects.order_by('-is_principale', 'ordre', 'id'),
            to_attr='profile_images',
        )
    ).order_by('-date_ajout')[:10]
    now = timezone.now()
    return render(request, 'accounts/profil_locataire.html', {
        'locataire': locataire,
        'favoris': favoris,
        'favoris_count': Favori.objects.filter(user=request.user).count(),
        'contacts_actifs_count': ContactDebloque.objects.filter(
            user=request.user, est_actif=True, date_expiration__gt=now
        ).count(),
        'messages_count': Message.objects.filter(destinataire=request.user).count(),
    })


@login_required
def profil_proprietaire_view(request):
    """Vue du profil propriétaire"""
    if request.user.role != 'proprietaire':
        return redirect(
            'accounts:profil_locataire'
            if request.user.role == 'locataire'
            else 'accounts:google_profile'
        )
    proprietaire, _ = Proprietaire.objects.get_or_create(user=request.user)
    annonce_queryset = proprietaire.annonces.all().order_by('-created_at')
    statut = request.GET.get('statut', '')
    statuts_valides = {choice[0] for choice in Annonce.STATUT_CHOICES}
    if statut in statuts_valides:
        annonce_queryset = annonce_queryset.filter(statut=statut)
    annonces_proprietaire = annonce_queryset.prefetch_related(
        Prefetch(
            'images',
            queryset=ImageAnnonce.objects.order_by('-is_principale', 'ordre', 'id'),
            to_attr='profile_images',
        )
    )[:10]
    latest_listing = proprietaire.annonces.order_by('-created_at').first()
    annonces_actives = proprietaire.annonces.filter(statut='active').count()
    total_vues = proprietaire.annonces.aggregate(total=Sum('nombre_vues'))['total'] or 0
    from paiements.models import Paiement
    revenus_30j = Paiement.objects.filter(
        annonce__proprietaire=proprietaire,
        statut='valide',
        date_paiement__gte=timezone.now() - timedelta(days=30),
    ).aggregate(total=Sum('montant'))['total'] or 0
    from messagerie.models import Message
    messages_recus = Message.objects.filter(destinataire=request.user).select_related(
        'expediteur', 'annonce'
    ).order_by('-date_envoi')[:15]
    messages_non_lus = Message.objects.filter(destinataire=request.user, lu=False).count()
    return render(request, 'accounts/profil_proprietaire.html', {
        'proprietaire': proprietaire,
        'annonces_actives': annonces_actives,
        'total_vues': total_vues,
        'revenus_30j': revenus_30j,
        'annonces_proprietaire': annonces_proprietaire,
        'latest_listing': latest_listing,
        'statut_filtre': statut,
        'messages_recus': messages_recus,
        'messages_non_lus': messages_non_lus,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def modifier_profil_view(request):
    """Modifier les informations de profil et préférences selon le rôle."""
    if request.user.role not in {'locataire', 'proprietaire'}:
        return redirect('accounts:google_profile')

    profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.user.role == 'locataire':
        preferences, _ = Locataire.objects.get_or_create(user=request.user)
        preferences_form = LocatairePreferencesForm(request.POST or None, instance=preferences)
    else:
        preferences, _ = Proprietaire.objects.get_or_create(user=request.user)
        preferences_form = ProprietairePreferencesForm(request.POST or None, instance=preferences)

    if request.method == 'POST':
        profile_valid = profile_form.is_valid()
        preferences_valid = preferences_form.is_valid()
        if profile_valid and preferences_valid:
            with transaction.atomic():
                profile_form.save()
                preferences_form.save()
            messages.success(request, 'Votre profil a été mis à jour.')
            return redirect(
                'accounts:profil_locataire'
                if request.user.role == 'locataire'
                else 'accounts:profil_proprietaire'
            )

    return render(request, 'accounts/profil_modifier.html', {
        'profile_form': profile_form,
        'preferences_form': preferences_form,
        'role_label': 'locataire' if request.user.role == 'locataire' else 'propriétaire',
    })


@require_POST
def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('annonces:index')
