from datetime import time, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .forms import ReservationWorkspaceForm
from .models import ConfigurationWorkspace, ReservationWorkspace


class ReservationWorkspaceModelTests(TestCase):
    def setUp(self):
        self.demain = timezone.localdate() + timedelta(days=1)

    def reservation(self, **overrides):
        data = {
            "nom": "Client Test",
            "email": "client@example.com",
            "telephone": "+243900000000",
            "date": self.demain,
            "heure_debut": time(9),
            "heure_fin": time(11, 30),
        }
        data.update(overrides)
        return ReservationWorkspace(**data)

    def test_calcul_duree_et_montant_en_decimal(self):
        reservation = self.reservation()
        reservation.save()
        self.assertEqual(reservation.duree_heures, Decimal("2.50"))
        self.assertEqual(reservation.montant_total, Decimal("1.25"))

    def test_str(self):
        reservation = self.reservation()
        self.assertEqual(str(reservation), f"Client Test - {self.demain}")

    def test_refuse_date_passee(self):
        reservation = self.reservation(date=timezone.localdate() - timedelta(days=1))
        with self.assertRaises(ValidationError):
            reservation.save()

    def test_refuse_fin_inferieure_ou_egale(self):
        reservation = self.reservation(heure_debut=time(10), heure_fin=time(10))
        with self.assertRaises(ValidationError):
            reservation.save()

    def test_refuse_horaire_hors_ouverture(self):
        reservation = self.reservation(heure_debut=time(7, 30), heure_fin=time(9))
        with self.assertRaises(ValidationError):
            reservation.save()

    def test_refuse_chevauchement(self):
        self.reservation(heure_debut=time(9), heure_fin=time(11)).save()
        autre = self.reservation(heure_debut=time(10), heure_fin=time(12))
        with self.assertRaises(ValidationError):
            autre.save()

    def test_accepte_creneaux_contigus(self):
        self.reservation(heure_debut=time(9), heure_fin=time(11)).save()
        autre = self.reservation(heure_debut=time(11), heure_fin=time(12))
        autre.save()
        self.assertEqual(ReservationWorkspace.objects.count(), 2)


class ReservationWorkspaceFormTests(TestCase):
    def test_erreurs_metier_visibles_dans_le_formulaire(self):
        form = ReservationWorkspaceForm(
            data={
                "nom": "Client Test",
                "email": "client@example.com",
                "telephone": "",
                "date": timezone.localdate() - timedelta(days=1),
                "heure_debut": "10:00",
                "heure_fin": "09:00",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)
        self.assertIn("heure_fin", form.errors)


class WorkspaceReservationViewTests(TestCase):
    def setUp(self):
        self.url = reverse("workspace")
        self.demain = timezone.localdate() + timedelta(days=1)
        self.data = {
            "nom": "Client Test",
            "email": "client@example.com",
            "telephone": "+243900000000",
            "date": self.demain.isoformat(),
            "heure_debut": "09:00",
            "heure_fin": "11:00",
        }

    def test_page_workspace(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Espace de travail")

    def test_reservation_valide_et_protection_double_soumission(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, self.url)
        self.assertEqual(ReservationWorkspace.objects.count(), 1)

        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ReservationWorkspace.objects.count(), 1)
        self.assertContains(response, "déjà réservée")

    def test_reservations_suspendues_masquent_et_bloquent_le_formulaire(self):
        ConfigurationWorkspace.objects.create(reservations_ouvertes=False)

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ReservationWorkspace.objects.count(), 0)
        self.assertContains(response, "Réservations suspendues")
        self.assertNotContains(response, "Réserver maintenant")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        EMAIL_HOST_USER="workspace@example.com",
        EMAIL_HOST_PASSWORD="test-password",
        DEFAULT_FROM_EMAIL="workspace@example.com",
    )
    def test_confirmation_email(self):
        self.client.post(self.url, self.data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["client@example.com"])

    @override_settings(
        EMAIL_HOST_USER="workspace@example.com",
        EMAIL_HOST_PASSWORD="test-password",
    )
    @patch("Workspace.views.send_mail", side_effect=RuntimeError("SMTP indisponible"))
    def test_echec_email_ne_supprime_pas_reservation(self, _send_mail):
        with self.assertLogs("mdtech", level="ERROR"):
            response = self.client.post(self.url, self.data)
        self.assertRedirects(response, self.url)
        self.assertEqual(ReservationWorkspace.objects.count(), 1)

# Create your tests here.
