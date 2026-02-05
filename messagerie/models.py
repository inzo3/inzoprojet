from django.db import models
from django.contrib.auth import get_user_model
from annonces.models import Annonce

User = get_user_model()


class Message(models.Model):
    """Modèle pour les messages entre utilisateurs"""
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_recus')
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='messages', blank=True, null=True)
    sujet = models.CharField(max_length=200, blank=True)
    contenu = models.TextField()
    lu = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['-date_envoi']
    
    def __str__(self):
        return f"Message de {self.expediteur.username} à {self.destinataire.username}"


class Favori(models.Model):
    """Modèle pour les annonces favorites"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoris')
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='favoris')
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        unique_together = ['user', 'annonce']
    
    def __str__(self):
        return f"{self.user.username} - {self.annonce.titre}"
