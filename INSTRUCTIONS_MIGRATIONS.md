# Instructions pour créer les migrations

## Problème
Les tables de la base de données n'existent pas encore. Il faut créer et appliquer les migrations.

## Solution

### Option 1 : Utiliser le script batch (Windows)
Double-cliquez sur `create_migrations.bat` dans le dossier `nzo_immo/nzo/`

### Option 2 : Commandes manuelles

1. **Activez l'environnement virtuel** :
```bash
cd nzo_immo\env\Scripts
activate
cd ..\..\nzo
```

2. **Créez les migrations** :
```bash
python manage.py makemigrations
```

3. **Appliquez les migrations** :
```bash
python manage.py migrate
```

4. **Créez un superutilisateur** (optionnel mais recommandé) :
```bash
python manage.py createsuperuser
```

## Vérification

Après avoir exécuté les migrations, vous devriez voir :
- Les tables créées dans votre base de données MySQL `nzo_db`
- Plus d'erreur "table n'existe pas"

## Note importante

Assurez-vous que :
1. MySQL est démarré
2. La base de données `nzo_db` existe (créez-la si nécessaire : `CREATE DATABASE nzo_db;`)
3. Les identifiants dans `settings.py` sont corrects
