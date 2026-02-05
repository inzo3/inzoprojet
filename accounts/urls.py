from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profil/locataire/', views.profil_locataire_view, name='profil_locataire'),
    path('profil/proprietaire/', views.profil_proprietaire_view, name='profil_proprietaire'),
]
