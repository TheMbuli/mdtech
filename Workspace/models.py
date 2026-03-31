from django.db import models
from datetime import datetime, date

class ReservationWorkspace(models.Model):

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

    def save(self, *args, **kwargs):
        PRIX_PAR_HEURE = 0.5  # 💰 fixé par toi

        debut = datetime.combine(date.today(), self.heure_debut)
        fin = datetime.combine(date.today(), self.heure_fin)

        minutes = (fin - debut).total_seconds() / 60
        self.duree_heures = round(minutes / 60, 2)

        self.montant_total = round(
            self.duree_heures * PRIX_PAR_HEURE,
            2
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} - {self.date}"
