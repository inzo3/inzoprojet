from django import forms

from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sujet', 'contenu']
        labels = {
            'sujet': 'Sujet',
            'contenu': 'Message',
        }
        widgets = {
            'sujet': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 200,
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Décrivez votre demande, dates de visite souhaitées...',
            }),
        }

    def clean_sujet(self):
        return (self.cleaned_data.get('sujet') or '').strip()

    def clean_contenu(self):
        contenu = (self.cleaned_data.get('contenu') or '').strip()
        if not contenu:
            raise forms.ValidationError('Écrivez un message avant de l’envoyer.')
        return contenu
