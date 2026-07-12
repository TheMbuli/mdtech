from datetime import datetime, time
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class ConfigurationWorkspace(models.Model):
    reservations_ouvertes = models.BooleanField(
        default=True,
        verbose_name="Réservations ouvertes",
        help_text="Décochez cette option pour suspendre les nouvelles réservations.",
    )

    class Meta:
        verbose_name = "Configuration des réservations"
        verbose_name_plural = "Configuration des réservations"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Réservations de l’espace"


class ReservationWorkspace(models.Model):
    PRIX_PAR_HEURE = Decimal("0.50")
    HEURE_OUVERTURE = time(8, 0)
    HEURE_FERMETURE = time(18, 0)

    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True)

    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    duree_heures = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        editable=False
    )

    montant_total = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Réservation espace"
        verbose_name_plural = "Réservations espace"
        constraints = [
            models.CheckConstraint(
                condition=Q(heure_fin__gt=F("heure_debut")),
                name="workspace_fin_apres_debut",
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}

        if self.date and self.date < timezone.localdate():
            errors["date"] = "La date de réservation ne peut pas être dans le passé."

        if self.heure_debut and self.heure_fin:
            if self.heure_fin <= self.heure_debut:
                errors["heure_fin"] = "L'heure de fin doit être supérieure à l'heure de début."
            elif (
                self.heure_debut < self.HEURE_OUVERTURE
                or self.heure_fin > self.HEURE_FERMETURE
            ):
                errors["heure_debut"] = (
                    "Les réservations sont possibles uniquement entre "
                    f"{self.HEURE_OUVERTURE:%H:%M} et {self.HEURE_FERMETURE:%H:%M}."
                )
            elif self.date:
                chevauchements = type(self).objects.filter(
                    date=self.date,
                    heure_debut__lt=self.heure_fin,
                    heure_fin__gt=self.heure_debut,
                )
                if self.pk:
                    chevauchements = chevauchements.exclude(pk=self.pk)
                if chevauchements.exists():
                    errors["heure_debut"] = "Cette plage horaire est déjà réservée."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        debut = datetime.combine(self.date, self.heure_debut)
        fin = datetime.combine(self.date, self.heure_fin)
        minutes = Decimal(str((fin - debut).total_seconds())) / Decimal("60")
        self.duree_heures = (minutes / Decimal("60")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        self.montant_total = (self.duree_heures * self.PRIX_PAR_HEURE).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} - {self.date}"
