from django.db import models
from django.core.validators import MinValueValidator

class Edition(models.Model):
    annee = models.PositiveIntegerField(
        unique=True,
        validators=[MinValueValidator(2022)],
    )

    class Meta:
        ordering = ["-annee"]

    def __str__(self):
        return f"Année {self.annee}"
    
class ImagesEdition(models.Model):
    edition = models.ForeignKey(
        Edition,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="images")

    def __str__(self):
        return f"Image de l'édition {self.edition.annee}"
