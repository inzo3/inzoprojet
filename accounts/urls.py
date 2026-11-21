from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('verification-email/envoye/', views.verification_sent_view, name='verification_sent'),
    path(
        'verification-email/renvoyer/',
        views.resend_verification_view,
        name='resend_verification',
    ),
    path(
        'verification-email/<uidb64>/<token>/',
        views.verify_email_view,
        name='verify_email',
    ),
    path(
        'mot-de-passe-oublie/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.txt',
            subject_template_name='registration/password_reset_subject.txt',
            success_url=reverse_lazy('accounts:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'mot-de-passe-oublie/envoye/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reinitialiser/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reinitialiser/termine/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
    path('google/profil/', views.google_profile_view, name='google_profile'),
    path('profil/modifier/', views.modifier_profil_view, name='modifier_profil'),
    path('profil/locataire/', views.profil_locataire_view, name='profil_locataire'),
    path('profil/proprietaire/', views.profil_proprietaire_view, name='profil_proprietaire'),
]
