from django import forms
from .models import Annonce


class AnnonceForm(forms.ModelForm):
    """Formulaire de création/édition d'une annonce"""

    class Meta:
        model = Annonce
        fields = [
            'titre', 'description', 'type_bien', 'prix', 'superficie',
            'nombre_chambres', 'nombre_salles_bain', 'ville', 'quartier', 'adresse',
            'latitude', 'longitude', 'is_meuble', 'is_premium',
        ]
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex : Bel appartement 3 pièces centre-ville'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Décrivez votre bien...'}),
            'type_bien': forms.Select(attrs={'class': 'form-select'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'FCFA / mois', 'min': 0}),
            'superficie': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm²', 'min': 0, 'step': '0.01'}),
            'nombre_chambres': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'nombre_salles_bain': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'ville': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex : Brazzaville'}),
            'quartier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex : Poto-Poto'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse détaillée (visible après déblocage)'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Optionnel', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Optionnel', 'step': 'any'}),
            'is_meuble': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_premium': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
