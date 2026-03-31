
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone

class Formation(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(max_length=1000)
    duree = models.DurationField(help_text="Durée de la formation (HH:MM:SS)")
    prix = models.PositiveIntegerField(help_text="Prix en dollars")
    affiche = models.ImageField(upload_to='formation_images', blank=True, null=True)
    objectifs = models.TextField(max_length=500)
    
    # Optionnel : dates de création et modification
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        # Générer automatiquement le slug si absent
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('formation_detail', kwargs={'slug': self.slug})


class Inscription(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='inscriptions')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True, null=True)
    date_inscription = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('formation', 'email')  # empêche doublon email + formation

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.formation.nom}"