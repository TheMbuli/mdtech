from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import InscriptionForm
from .models import Formation, Inscription


def creer_formation(nom="Formation BIM"):
    return Formation.objects.create(
        nom=nom,
        description="Description de la formation",
        duree=20,
        objectifs="Maîtriser les outils essentiels.",
        logo="logo/test.png",
    )


class FormationModelTests(TestCase):
    def test_creation_slug(self):
        formation = creer_formation("Modélisation BIM avancée")
        self.assertEqual(formation.slug, "modelisation-bim-avancee")

    def test_collision_slug_genere_suffixe(self):
        premiere = creer_formation("C++")
        seconde = creer_formation("C--")
        self.assertEqual(premiere.slug, "c")
        self.assertEqual(seconde.slug, "c-2")

    def test_str_inscription(self):
        formation = creer_formation()
        inscription = Inscription(
            formation=formation,
            nom="Mubake",
            prenom="Eddy",
            email="eddy@example.com",
        )
        self.assertEqual(str(inscription), "Mubake Eddy - Formation BIM")


class InscriptionFormTests(TestCase):
    def setUp(self):
        self.formation = creer_formation()

    def form(self, **overrides):
        data = {
            "nom": "Mubake",
            "prenom": "Eddy",
            "email": "EDDY@EXAMPLE.COM",
            "telephone": "+243 990 000 000",
        }
        data.update(overrides)
        form = InscriptionForm(data=data)
        form.instance.formation = self.formation
        return form

    def test_normalise_email(self):
        form = self.form()
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["email"], "eddy@example.com")

    def test_refuse_telephone_invalide(self):
        form = self.form(telephone="abc")
        self.assertFalse(form.is_valid())
        self.assertIn("telephone", form.errors)

    def test_refuse_double_inscription_independamment_de_la_casse(self):
        Inscription.objects.create(
            formation=self.formation,
            nom="Mubake",
            prenom="Eddy",
            email="eddy@example.com",
        )
        form = self.form(email="EDDY@example.com")
        self.assertFalse(form.is_valid())
        self.assertIn("déjà inscrit", form.errors["email"][0])


class InscriptionViewTests(TestCase):
    def setUp(self):
        self.formation = creer_formation()
        self.url = reverse("formation_inscription", args=[self.formation.slug])
        self.data = {
            "nom": "Mubake",
            "prenom": "Eddy",
            "email": "eddy@example.com",
            "telephone": "+243 990 000 000",
        }

    def test_inscription_valide_utilise_post_redirect_get(self):
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, self.url)
        self.assertEqual(Inscription.objects.count(), 1)
        self.assertContains(response, "Inscription réussie")

    def test_double_soumission_ne_cree_pas_de_doublon(self):
        self.client.post(self.url, self.data)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inscription.objects.count(), 1)
        self.assertContains(response, "déjà inscrit")

    def test_formation_suspendue_masque_le_formulaire(self):
        self.formation.inscriptions_ouvertes = False
        self.formation.save(update_fields=["inscriptions_ouvertes"])

        response = self.client.get(self.url)

        self.assertContains(response, "Inscriptions suspendues")
        self.assertNotContains(response, 'id="inscriptionForm"')

    def test_formation_suspendue_refuse_aussi_une_soumission_directe(self):
        self.formation.inscriptions_ouvertes = False
        self.formation.save(update_fields=["inscriptions_ouvertes"])

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inscription.objects.count(), 0)
        self.assertContains(response, "Inscriptions suspendues")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        EMAIL_HOST_USER="site@example.com",
        EMAIL_HOST_PASSWORD="test-password",
        DEFAULT_FROM_EMAIL="site@example.com",
        ADMIN_EMAIL="admin@example.com",
    )
    def test_envoie_notification_admin_et_confirmation(self):
        self.client.post(self.url, self.data)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["admin@example.com"])
        self.assertEqual(mail.outbox[1].to, ["eddy@example.com"])

    @override_settings(
        EMAIL_HOST_USER="site@example.com",
        EMAIL_HOST_PASSWORD="test-password",
        ADMIN_EMAIL="admin@example.com",
    )
    @patch("Formation.views.send_mail", side_effect=RuntimeError("SMTP indisponible"))
    def test_echec_email_conserve_inscription(self, _send_mail):
        with self.assertLogs("mdtech", level="ERROR"):
            response = self.client.post(self.url, self.data)
        self.assertRedirects(response, self.url)
        self.assertEqual(Inscription.objects.count(), 1)

# Create your tests here.
