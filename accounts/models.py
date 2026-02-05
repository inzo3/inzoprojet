from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Modèle utilisateur étendu"""
    ROLE_CHOICES = [
        ('locataire', 'Locataire'),
        ('proprietaire', 'Propriétaire'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"


class Proprietaire(models.Model):
    """Profil détaillé du propriétaire"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='proprietaire')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_avis = models.IntegerField(default=0)
    zone_principale = models.CharField(max_length=200, blank=True)
    temps_reponse = models.CharField(max_length=50, blank=True)
    is_premium = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Propriétaire"
        verbose_name_plural = "Propriétaires"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Propriétaire"


class Locataire(models.Model):
    """Profil détaillé du locataire"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='locataire')
    ville_preferee = models.CharField(max_length=100, blank=True)
    quartier_prefere = models.CharField(max_length=100, blank=True)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Locataire"
        verbose_name_plural = "Locataires"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Locataire"
