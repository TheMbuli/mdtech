from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from .models import Edition, ImagesEdition


class EditionModelTests(TestCase):
    def test_annee_minimale(self):
        with self.assertRaises(ValidationError):
            Edition(annee=2021).full_clean()

    def test_annee_unique(self):
        Edition.objects.create(annee=2026)
        with self.assertRaises(IntegrityError):
            Edition.objects.create(annee=2026)

    def test_relation_images(self):
        edition = Edition.objects.create(annee=2026)
        image = ImagesEdition.objects.create(edition=edition, image="images/test.jpg")
        self.assertEqual(edition.images.get(), image)
        self.assertEqual(str(image), "Image de l'édition 2026")

# Create your tests here.
