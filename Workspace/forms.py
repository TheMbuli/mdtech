from django import forms
from .models import ReservationWorkspace

class ReservationWorkspaceForm(forms.ModelForm):

    class Meta:
        model = ReservationWorkspace
        fields = [
            "nom",
            "email",
            "telephone",
            "date",
            "heure_debut",
            "heure_fin",
        ]

        widgets = {
            "nom": forms.TextInput(attrs={
                "class": "w-full px-3 py-2 bg-white text-blue-900 border border-blue-300"
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-3 py-2 bg-white text-blue-900 border border-blue-300"
            }),
            "telephone": forms.TextInput(attrs={
                "class": "w-full px-3 py-2 bg-white text-blue-900 border border-blue-300"
            }),
            "date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full px-3 py-2 bg-white text-blue-900 border border-blue-300"
            }),
            "heure_debut": forms.TimeInput(attrs={
                "type": "time",
                "class": "w-full px-3 py-2 bg-white text-blue-900 border border-blue-300"
            }),
            "heure_fin": forms.TimeInput(attrs={
                "type": "time",
                "class": "w-full px-3 py-2 bg-white text-blue-900 border border-blue-300"
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        debut = cleaned_data.get("heure_debut")
        fin = cleaned_data.get("heure_fin")

        if debut and fin and fin <= debut:
            raise forms.ValidationError(
                "L'heure de fin doit être supérieure à l'heure de début."
            )

        return cleaned_data
