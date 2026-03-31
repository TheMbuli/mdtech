from django.db import models

# Create your models here.


class Article(models.Model):
    nom = models.CharField(max_length=50)
    description = models.TextField(max_length=300)
    prix = models.IntegerField(default=0)
    reduction = models.IntegerField(default=0)

class PhotoArticle(models.Model):
    image = models.ImageField(upload_to='photo_article')
    article = models.ForeignKey(Article,on_delete=models.CASCADE)