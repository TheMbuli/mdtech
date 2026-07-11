from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Article, PhotoArticle


class ArticleModelTests(TestCase):
    def test_prix_final(self):
        article = Article(prix=Decimal("100.00"), reduction=Decimal("15.50"))
        self.assertEqual(article.prix_final, Decimal("84.50"))

    def test_str(self):
        self.assertEqual(str(Article(nom="Plan architectural")), "Plan architectural")

    def test_refuse_prix_negatif(self):
        article = Article(
            nom="Article",
            description="Description",
            prix=Decimal("-1.00"),
        )
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_refuse_reduction_superieure_au_prix(self):
        article = Article(
            nom="Article",
            description="Description",
            prix=Decimal("10.00"),
            reduction=Decimal("11.00"),
        )
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_relation_photos(self):
        article = Article.objects.create(
            nom="Article",
            description="Description",
            prix=Decimal("10.00"),
        )
        photo = PhotoArticle.objects.create(article=article, image="photo_article/test.jpg")
        self.assertEqual(article.photos.get(), photo)

# Create your tests here.
