from django import forms

from .models import Inscription


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['nom', 'prenom', 'email', 'telephone']

        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full pl-14 pr-4 py-4 rounded-2xl bg-white border border-slate-200 focus:border-blue-700 focus:ring-4 focus:ring-blue-100 outline-none transition  text-slate-700',
                'placeholder': 'Votre nom'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'w-full pl-14 pr-6 py-4 rounded-2xl bg-white border border-slate-200 focus:border-blue-700 focus:ring-4 focus:ring-blue-100 outline-none transition  text-slate-700',
                'placeholder': 'Votre prénom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full pl-14 pr-6 py-4 rounded-2xl bg-white border border-slate-200 focus:border-blue-700 focus:ring-4 focus:ring-blue-100 outline-none transition  text-slate-700',
                'placeholder': 'exemple@gmail.com'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'w-full pl-14 pr-6 py-4 rounded-2xl bg-white border border-slate-200 focus:border-blue-700 focus:ring-4 focus:ring-blue-100 outline-none transition text-slate-700',
                'placeholder': '+243 ...'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        formation_id = self.instance.formation_id
        if formation_id and Inscription.objects.filter(
            formation_id=formation_id,
            email__iexact=email,
        ).exists():
            raise forms.ValidationError(
                "Vous êtes déjà inscrit à cette formation avec cet email."
            )
        return email
