"""
Script pour nettoyer et réinitialiser les migrations
À exécuter si vous avez des erreurs de conflit avec le modèle User
"""
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Supprimer db.sqlite3
db_file = BASE_DIR / 'db.sqlite3'
if db_file.exists():
    print(f"Suppression de {db_file}")
    db_file.unlink()

# Supprimer les dossiers migrations (sauf __init__.py)
for app in ['accounts', 'annonces', 'paiements', 'messagerie']:
    migrations_dir = BASE_DIR / app / 'migrations'
    if migrations_dir.exists():
        print(f"Nettoyage de {migrations_dir}")
        for file in migrations_dir.iterdir():
            if file.name != '__init__.py':
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    shutil.rmtree(file)

print("\nNettoyage terminé. Exécutez maintenant:")
print("  python manage.py makemigrations")
print("  python manage.py migrate")
