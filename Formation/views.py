import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView
from django.views.generic.list import ListView

from .forms import InscriptionForm
from .models import Formation

logger = logging.getLogger("mdtech")


class FormationListView(ListView):
    model = Formation
    template_name = 'Formation/formation.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


class FormationDetailView(DetailView):
    model = Formation
    template_name = 'Formation/details_formation.html'
    context_object_name = 'formation'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


def inscription_view(request, slug):
    formation = get_object_or_404(Formation, slug=slug)
    inscription_reussie = False

    if request.method == "POST" and not formation.inscriptions_ouvertes:
        form = InscriptionForm()
    elif request.method == "POST":
        form = InscriptionForm(request.POST)
        form.instance.formation = formation

        if form.is_valid():
            try:
                with transaction.atomic():
                    inscription = form.save()
            except IntegrityError:
                form.add_error(
                    "email",
                    "Vous êtes déjà inscrit à cette formation avec cet email.",
                )
            else:
                envoyer_notifications_inscription(inscription)
                request.session["inscription_reussie"] = True
                return redirect("formation_inscription", slug=formation.slug)
    else:
        form = InscriptionForm()
        inscription_reussie = request.session.pop("inscription_reussie", False)

    return render(request, 'Formation/inscription.html', {
        'form': form,
        'formation': formation,
        'inscription_reussie': inscription_reussie
    })


def envoyer_notifications_inscription(inscription):
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        return

    messages = []
    if settings.ADMIN_EMAIL:
        messages.append((
            f"Nouvelle inscription à la formation : {inscription.formation.nom}",
            f"""\
Une nouvelle personne vient de s'inscrire à la formation.

Formation : {inscription.formation.nom}

Nom : {inscription.nom}
Email : {inscription.email}
Téléphone : {inscription.telephone}

Merci de la contacter pour la suite de l'inscription.
""",
            [settings.ADMIN_EMAIL],
        ))
    messages.append((
        "Confirmation de votre inscription",
        f"""\
Bonjour {inscription.nom},

Votre inscription à la formation "{inscription.formation.nom}" a bien été enregistrée.

Pour finaliser votre inscription, veuillez contacter l'admin du site Modern Technology of Building.

Email : {settings.ADMIN_EMAIL}

Merci pour votre confiance.

Modern Technology of Building
""",
        [inscription.email],
    ))

    for subject, message, recipients in messages:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                "Échec d'une notification pour l'inscription à la formation %s.",
                inscription.formation_id,
            )
