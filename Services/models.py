from django.db import models

class Service(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    pricing = models.TextField(max_length=500)
    

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ["nom"]


class PhotoService(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="services")

    def __str__(self):
        return f"Photo du service {self.service.nom}"
