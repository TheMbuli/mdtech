from django.test import TestCase

from .models import PhotoProjet, Projet


class ProjetModelTests(TestCase):
    def test_relation_et_representations(self):
        projet = Projet.objects.create(
            titre="Immeuble moderne",
            description="Description",
            affiche="projet/affiche/test.jpg",
        )
        photo = PhotoProjet.objects.create(projet=projet, image="projets/test.jpg")
        self.assertEqual(str(projet), "Immeuble moderne")
        self.assertEqual(str(photo), "Photo du projet Immeuble moderne")
        self.assertEqual(projet.photos.get(), photo)

# Create your tests here.
