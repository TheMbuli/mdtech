from django import forms
from django.utils import timezone

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
                "min": timezone.localdate().isoformat(),
                "class": "w-full px-3 py-2 bg-white text-blue-900 border border-blue-300"
            }),
            "heure_debut": forms.TimeInput(attrs={
                "type": "time",
                "min": ReservationWorkspace.HEURE_OUVERTURE.strftime("%H:%M"),
                "max": ReservationWorkspace.HEURE_FERMETURE.strftime("%H:%M"),
                "class": "w-full px-3 py-2 bg-white text-blue-900 border border-blue-300"
            }),
            "heure_fin": forms.TimeInput(attrs={
                "type": "time",
                "min": ReservationWorkspace.HEURE_OUVERTURE.strftime("%H:%M"),
                "max": ReservationWorkspace.HEURE_FERMETURE.strftime("%H:%M"),
                "class": "w-full px-3 py-2 bg-white text-blue-900 border border-blue-300"
            }),
        }
