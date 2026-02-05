"""
Script pour vérifier que les modèles sont bien détectés
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzo.settings')
django.setup()

from django.apps import apps

print("Applications installées:")
for app in apps.get_app_configs():
    print(f"  - {app.name}")

print("\nModèles détectés:")
for model in apps.get_models():
    print(f"  - {model._meta.app_label}.{model.__name__}")

print("\nModèles de accounts:")
try:
    from accounts.models import User, Proprietaire, Locataire
    print(f"  - User: {User}")
    print(f"  - Proprietaire: {Proprietaire}")
    print(f"  - Locataire: {Locataire}")
except Exception as e:
    print(f"  ERREUR: {e}")

print("\nModèles de annonces:")
try:
    from annonces.models import Annonce, ImageAnnonce
    print(f"  - Annonce: {Annonce}")
    print(f"  - ImageAnnonce: {ImageAnnonce}")
except Exception as e:
    print(f"  ERREUR: {e}")
