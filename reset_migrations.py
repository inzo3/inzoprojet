"""
Script pour réinitialiser complètement les migrations
ATTENTION: Ce script supprime toutes les données de la base de données
"""
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

print("⚠️  ATTENTION: Ce script va supprimer toutes les migrations et la base de données!")
print("Toutes les données seront perdues.\n")

response = input("Voulez-vous continuer? (oui/non): ")
if response.lower() != 'oui':
    print("Annulé.")
    exit()

# Supprimer db.sqlite3 si existe
db_file = BASE_DIR / 'db.sqlite3'
if db_file.exists():
    print(f"Suppression de {db_file}")
    db_file.unlink()

# Supprimer tous les fichiers de migrations (sauf __init__.py)
for app in ['accounts', 'annonces', 'paiements', 'messagerie']:
    migrations_dir = BASE_DIR / app / 'migrations'
    if migrations_dir.exists():
        print(f"Nettoyage de {migrations_dir}")
        for file in migrations_dir.iterdir():
            if file.name != '__init__.py':
                if file.is_file():
                    print(f"  Suppression: {file.name}")
                    file.unlink()
                elif file.is_dir():
                    print(f"  Suppression du dossier: {file.name}")
                    shutil.rmtree(file)

print("\n✅ Nettoyage terminé!")
print("\n📝 Prochaines étapes:")
print("1. Supprimez manuellement les tables dans MySQL (ou recréez la base de données)")
print("2. Exécutez: python manage.py makemigrations")
print("3. Exécutez: python manage.py migrate")
print("\nOu pour MySQL:")
print("  DROP DATABASE nzo_db;")
print("  CREATE DATABASE nzo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
print("  python manage.py makemigrations")
print("  python manage.py migrate")
