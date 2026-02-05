@echo off
echo Activation de l'environnement virtuel...
call ..\env\Scripts\activate.bat

echo Creation des migrations...
python manage.py makemigrations

echo.
echo Application des migrations...
python manage.py migrate

echo.
echo Migrations terminees!
pause
