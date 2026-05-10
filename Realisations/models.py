from django.db import models
from django.urls import reverse

class Projet(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    date_creation = models.DateField(auto_now_add=True)
    affiche = models.ImageField(upload_to="projet/affiche/")

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('details-projet', args=[self.id])


class PhotoProjet(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to='projets/')

    def __str__(self):
        return f"Photo du projet {self.projet.titre}"
