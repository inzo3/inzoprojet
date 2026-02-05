# Configuration du projet LocaHome Django

## Étape 1 : Configuration finale de settings.py

Ajoutez ces lignes dans `nzo_immo/nzo/nzo/settings.py` :

```python
# Après la ligne 123 (USE_TZ = True)
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Brazzaville'

# Après WSGI_APPLICATION
AUTH_USER_MODEL = 'accounts.User'
```

## Étape 2 : Création des migrations et de la base de données

```bash
cd nzo_immo/nzo
python manage.py makemigrations
python manage.py migrate
```

## Étape 3 : Création d'un superutilisateur

```bash
python manage.py createsuperuser
```

## Étape 4 : Copie des templates HTML

Les templates HTML originaux doivent être adaptés pour Django. Les templates de base sont créés dans `templates/`. 

Pour les autres pages (index, annonce_detail, profils), vous pouvez :
1. Copier le contenu HTML original
2. L'adapter avec les tags Django ({% extends %}, {% block %}, {% url %}, etc.)
3. Utiliser les variables passées par les vues

## Structure des templates

- `templates/base.html` - Template de base
- `templates/accounts/login.html` - Page de connexion
- `templates/accounts/register.html` - Page d'inscription
- `templates/accounts/profil_locataire.html` - Profil locataire (à créer)
- `templates/accounts/profil_proprietaire.html` - Profil propriétaire (à créer)
- `templates/annonces/index.html` - Page d'accueil (à créer)
- `templates/annonces/annonce_detail.html` - Détail d'annonce (à créer)
- `templates/paiements/paiement.html` - Page de paiement (à créer)

## Applications créées

1. **accounts** - Gestion des utilisateurs (User, Proprietaire, Locataire)
2. **annonces** - Gestion des annonces immobilières
3. **paiements** - Gestion des paiements Mobile Money
4. **messagerie** - Messages et favoris

## URLs configurées

- `/` - Page d'accueil (annonces:index)
- `/annonce/<id>/` - Détail d'une annonce
- `/recherche/` - Recherche d'annonces
- `/compte/login/` - Connexion
- `/compte/register/` - Inscription
- `/compte/profil/locataire/` - Profil locataire
- `/compte/profil/proprietaire/` - Profil propriétaire
- `/paiement/<annonce_id>/` - Paiement pour débloquer contact
- `/messagerie/favori/ajouter/<id>/` - Ajouter aux favoris
- `/admin/` - Interface d'administration

## Fichiers statiques

Les fichiers CSS sont dans `static/css/` :
- `styles.css` - Styles principaux
- `auth.css` - Styles pour l'authentification

## Prochaines étapes

1. Adapter tous les templates HTML pour Django
2. Implémenter la logique de paiement avec l'API Mobile Money
3. Ajouter la gestion des images (Pillow nécessaire)
4. Configurer les médias pour les uploads
5. Ajouter des tests unitaires
6. Configurer pour la production (ALLOWED_HOSTS, SECRET_KEY, etc.)
