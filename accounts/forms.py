from django import forms
from decimal import Decimal

from .models import Locataire, Proprietaire, User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'phone': 'Téléphone',
            'avatar': 'Photo de profil',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'tel'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class LocatairePreferencesForm(forms.ModelForm):
    class Meta:
        model = Locataire
        fields = ['ville_preferee', 'quartier_prefere', 'budget_min', 'budget_max']
        labels = {
            'ville_preferee': 'Ville préférée',
            'quartier_prefere': 'Quartier préféré',
            'budget_min': 'Budget mensuel minimum (FCFA)',
            'budget_max': 'Budget mensuel maximum (FCFA)',
        }
        widgets = {
            'ville_preferee': forms.TextInput(attrs={'class': 'form-control'}),
            'quartier_prefere': forms.TextInput(attrs={'class': 'form-control'}),
            'budget_min': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'budget_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['budget_min'].required = False
        self.fields['budget_max'].required = False

    def clean(self):
        cleaned_data = super().clean()
        budget_min = cleaned_data.get('budget_min')
        budget_max = cleaned_data.get('budget_max')
        if budget_min is None:
            cleaned_data['budget_min'] = Decimal('0')
            budget_min = Decimal('0')
        if budget_max is None:
            cleaned_data['budget_max'] = Decimal('0')
            budget_max = Decimal('0')
        if budget_max and budget_min > budget_max:
            self.add_error('budget_max', 'Le budget maximum doit être supérieur ou égal au minimum.')
        return cleaned_data


class ProprietairePreferencesForm(forms.ModelForm):
    class Meta:
        model = Proprietaire
        fields = ['zone_principale', 'temps_reponse']
        labels = {
            'zone_principale': 'Zone principale',
            'temps_reponse': 'Délai moyen de réponse',
        }
        widgets = {
            'zone_principale': forms.TextInput(attrs={'class': 'form-control'}),
            'temps_reponse': forms.TextInput(attrs={'class': 'form-control'}),
        }
