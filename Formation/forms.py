from django import forms
from .models import Inscription

class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['nom', 'prenom', 'email', 'telephone']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'w-full px-3 py-2 bg-white text-blue-900 border border-blue-300'}),
            'prenom': forms.TextInput(attrs={'class': 'w-full px-3 py-2 bg-white text-blue-900 border border-blue-300'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 bg-white text-blue-900 border border-blue-300'}),
            'telephone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 bg-white text-blue-900 border border-blue-300'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        formation = self.instance.formation if self.instance.pk else self.initial.get('formation')
        if Inscription.objects.filter(email=email, formation=formation).exists():
            raise forms.ValidationError("Vous êtes déjà inscrit à cette formation avec cet email.")
        return email
