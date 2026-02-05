# Instructions pour réinitialiser la base de données

## Problème
Les migrations ont été créées avec le modèle User par défaut, mais nous utilisons maintenant un modèle User personnalisé. Il faut réinitialiser.

## Solution 1 : Réinitialiser MySQL (Recommandé)

### Étape 1 : Supprimer et recréer la base de données

Connectez-vous à MySQL et exécutez :

```sql
DROP DATABASE IF EXISTS nzo_db;
CREATE DATABASE nzo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Étape 2 : Supprimer les fichiers de migrations

Exécutez le script Python :
```bash
python reset_migrations.py
```

Ou manuellement, supprimez tous les fichiers dans :
- `accounts/migrations/` (sauf `__init__.py`)
- `annonces/migrations/` (sauf `__init__.py`)
- `paiements/migrations/` (sauf `__init__.py`)
- `messagerie/migrations/` (sauf `__init__.py`)

### Étape 3 : Recréer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Étape 4 : Créer un superutilisateur

```bash
python manage.py createsuperuser
```

## Solution 2 : Marquer les migrations comme non appliquées (Avancé)

Si vous voulez garder certaines données, vous pouvez marquer les migrations comme non appliquées :

```bash
python manage.py migrate --fake accounts zero
python manage.py migrate --fake annonces zero
python manage.py migrate --fake paiements zero
python manage.py migrate --fake messagerie zero
```

Puis supprimez les fichiers de migrations et recréez-les.

## Vérification

Après avoir exécuté les migrations, vérifiez que les tables existent :

```sql
USE nzo_db;
SHOW TABLES;
```

Vous devriez voir des tables comme :
- accounts_user
- accounts_proprietaire
- accounts_locataire
- annonces_annonce
- annonces_imageannonce
- etc.
