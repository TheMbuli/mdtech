from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q


class Article(models.Model):
    nom = models.CharField(max_length=50)
    description = models.TextField(max_length=300)
    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    reduction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        ordering = ["nom"]
        constraints = [
            models.CheckConstraint(
                condition=Q(reduction__lte=F("prix")),
                name="boutique_reduction_inferieure_prix",
            ),
        ]

    @property
    def prix_final(self):
        return self.prix - self.reduction

    def __str__(self):
        return self.nom


class PhotoArticle(models.Model):
    image = models.ImageField(upload_to='photo_article')
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="photos",
    )

    def __str__(self):
        return f"Photo de {self.article.nom}"
