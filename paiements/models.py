from django.db import models
from django.contrib.auth import get_user_model
from annonces.models import Annonce

User = get_user_model()


class Paiement(models.Model):
    """Modèle pour les paiements Mobile Money"""
    METHODE_CHOICES = [
        ('mtn', 'MTN Money'),
        ('airtel', 'Airtel Money'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('echec', 'Échec'),
        ('rembourse', 'Remboursé'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paiements')
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode = models.CharField(max_length=20, choices=METHODE_CHOICES)
    numero_telephone = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_paiement = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"Paiement {self.montant} FCFA - {self.user.username}"


class ContactDebloque(models.Model):
    """Enregistrement des contacts débloqués"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts_debloques')
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='contacts_debloques')
    paiement = models.OneToOneField(Paiement, on_delete=models.CASCADE, related_name='contact_debloque')
    date_deblocage = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField()
    est_actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Contact débloqué"
        verbose_name_plural = "Contacts débloqués"
        unique_together = ['user', 'annonce']
    
    def __str__(self):
        return f"Contact débloqué - {self.user.username} - {self.annonce.titre}"
