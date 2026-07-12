import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import ReservationWorkspaceForm
from .models import ConfigurationWorkspace, ReservationWorkspace

logger = logging.getLogger("mdtech")


class WorkspaceReservationView(FormView):
    template_name = "Workspace/workspace.html"
    form_class = ReservationWorkspaceForm
    success_url = reverse_lazy("workspace")

    def reservations_ouvertes(self):
        return ConfigurationWorkspace.objects.filter(pk=1).values_list(
            "reservations_ouvertes", flat=True
        ).first() is not False

    def post(self, request, *args, **kwargs):
        if not self.reservations_ouvertes():
            return self.render_to_response(self.get_context_data())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        reservation = form.save()
        self.request.session["reservation_reussie"] = True
        self._envoyer_confirmation(reservation)
        return super().form_valid(form)

    @staticmethod
    def _envoyer_confirmation(reservation):
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            return
        try:
            send_mail(
                subject="Confirmation de votre réservation Workspace",
                message=(
                    f"Bonjour {reservation.nom},\n\n"
                    "Votre réservation a bien été enregistrée pour le "
                    f"{reservation.date:%d/%m/%Y}, de "
                    f"{reservation.heure_debut:%H:%M} à {reservation.heure_fin:%H:%M}.\n"
                    f"Montant total : {reservation.montant_total} $.\n\n"
                    "Modern Technology of Building"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reservation.email],
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                "Échec de l'envoi de la confirmation Workspace pour la réservation %s.",
                reservation.pk,
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prix_heure"] = ReservationWorkspace.PRIX_PAR_HEURE
        context["prix_heure_js"] = format(ReservationWorkspace.PRIX_PAR_HEURE, "f")
        context["heure_ouverture"] = ReservationWorkspace.HEURE_OUVERTURE
        context["heure_fermeture"] = ReservationWorkspace.HEURE_FERMETURE
        context["reservation_reussie"] = self.request.session.pop(
            "reservation_reussie", False
        )
        context["reservations_ouvertes"] = self.reservations_ouvertes()
        return context
