from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Proprietaire

User = get_user_model()


class Annonce(models.Model):
    """Modèle pour les annonces immobilières"""
    TYPE_CHOICES = [
        ('appartement', 'Appartement'),
        ('maison', 'Maison'),
        ('studio', 'Studio'),
        ('villa', 'Villa'),
    ]
    
    STATUT_CHOICES = [
        ('active', 'Active'),
        ('en_attente', 'En attente'),
        ('desactivee', 'Désactivée'),
        ('louee', 'Louée'),
    ]
    
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.CASCADE, related_name='annonces')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    type_bien = models.CharField(max_length=20, choices=TYPE_CHOICES)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    superficie = models.DecimalField(max_digits=8, decimal_places=2)
    nombre_chambres = models.IntegerField()
    nombre_salles_bain = models.IntegerField()
    ville = models.CharField(max_length=100)
    quartier = models.CharField(max_length=100)
    adresse = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_meuble = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    nombre_vues = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Annonce"
        verbose_name_plural = "Annonces"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titre} - {self.ville}"


class ImageAnnonce(models.Model):
    """Images associées à une annonce"""
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='annonces/')
    is_principale = models.BooleanField(default=False)
    ordre = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
        ordering = ['ordre', 'id']
    
    def __str__(self):
        return f"Image {self.ordre} - {self.annonce.titre}"


class Equipement(models.Model):
    """Équipements disponibles dans un bien"""
    nom = models.CharField(max_length=100)
    icone = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = "Équipement"
        verbose_name_plural = "Équipements"
    
    def __str__(self):
        return self.nom


class AnnonceEquipement(models.Model):
    """Relation entre annonce et équipements"""
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='equipements')
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ['annonce', 'equipement']
        verbose_name = "Équipement de l'annonce"
        verbose_name_plural = "Équipements des annonces"
