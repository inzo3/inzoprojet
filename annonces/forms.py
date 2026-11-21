from django import forms
from .models import Annonce


class AnnonceForm(forms.ModelForm):
    """Formulaire de création/édition d'une annonce"""

    class Meta:
        model = Annonce
        fields = [
            'titre', 'description', 'type_bien', 'prix', 'superficie',
            'nombre_chambres', 'nombre_salles_bain', 'ville', 'quartier', 'adresse',
            'latitude', 'longitude', 'is_meuble',
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
        }

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        if (latitude is None) != (longitude is None):
            raise forms.ValidationError(
                'Indiquez la latitude et la longitude ensemble, ou laissez les deux champs vides.'
            )
        prix = cleaned_data.get('prix')
        superficie = cleaned_data.get('superficie')
        nombre_chambres = cleaned_data.get('nombre_chambres')
        nombre_salles_bain = cleaned_data.get('nombre_salles_bain')
        if prix is not None and prix <= 0:
            self.add_error('prix', 'Le prix doit être supérieur à zéro.')
        if superficie is not None and superficie <= 0:
            self.add_error('superficie', 'La superficie doit être supérieure à zéro.')
        if nombre_chambres is not None and nombre_chambres < 0:
            self.add_error('nombre_chambres', 'Le nombre de chambres ne peut pas être négatif.')
        if nombre_salles_bain is not None and nombre_salles_bain < 0:
            self.add_error('nombre_salles_bain', 'Le nombre de salles de bain ne peut pas être négatif.')
        return cleaned_data
