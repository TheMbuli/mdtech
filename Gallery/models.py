from django.db import models
from django.core.validators import MinValueValidator

class Edition(models.Model):
    annee = models.PositiveIntegerField(validators=[MinValueValidator(2022)])

    def __str__(self):
        return f"Année {self.annee}"
    
class ImagesEdition(models.Model):
    edition = models.ForeignKey(Edition, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images")