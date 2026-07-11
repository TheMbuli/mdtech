
from decimal import Decimal

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import F
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


telephone_validator = RegexValidator(
    regex=r"^\+?[0-9][0-9 .()-]{6,19}$",
    message="Saisissez un numéro de téléphone valide.",
)


class Formation(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(max_length=1000)
    duree = models.PositiveBigIntegerField()
    prix_pro = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Prix pro",
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    prix_etudiant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Prix étudiant",
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    affiche = models.ImageField(upload_to='formation_images', blank=True, null=True)
    objectifs = models.TextField(max_length=500)
    logo = models.ImageField(upload_to="logo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nom) or "formation"
            slug = base_slug[:120]
            suffixe = 2
            while Formation.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                marqueur = f"-{suffixe}"
                slug = f"{base_slug[:120 - len(marqueur)]}{marqueur}"
                suffixe += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('formation_detail', kwargs={'slug': self.slug})


class Inscription(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='inscriptions')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[telephone_validator],
    )
    date_inscription = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                F("formation"),
                name="formation_email_inscription_unique",
            ),
        ]
        ordering = ["-date_inscription"]

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.formation.nom}"
from decimal import Decimal

from django.core.validators import MinValueValidator
