from django.views.generic.list import ListView
from django.views.generic import DetailView
from .models import Formation, Inscription
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .forms import InscriptionForm
from django.core.mail import send_mail
from django.conf import settings


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

    if request.method == "POST":
        form = InscriptionForm(request.POST)
        form.instance.formation = formation

        email = form.data.get('email')

        if Inscription.objects.filter(email=email, formation=formation).exists():
            form.add_error('email', "Vous êtes déjà inscrit à cette formation avec cet email.")

        elif form.is_valid():
            inscription = form.save()
            inscription_reussie = True

            # Mail envoyé à l'admin
            send_mail(
                subject=f"Nouvelle inscription à la formation : {formation.nom}",
                message=f"""
Une nouvelle personne vient de s'inscrire à la formation.

Formation : {formation.nom}

Nom : {inscription.nom}
Email : {inscription.email}
Téléphone : {inscription.telephone}

Merci de la contacter pour la suite de l'inscription.
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )

            # Mail de confirmation envoyé à l'inscrit
            send_mail(
                subject="Confirmation de votre inscription",
                message=f"""
Bonjour {inscription.nom},

Votre inscription à la formation "{formation.nom}" a bien été enregistrée.

Pour finaliser votre inscription, veuillez contacter l'admin du site Modern Technology of Building.

Email : {settings.ADMIN_EMAIL}

Merci pour votre confiance.

Modern Technology of Building
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[inscription.email],
                fail_silently=False,
            )

    else:
        form = InscriptionForm()

    return render(request, 'Formation/inscription.html', {
        'form': form,
        'formation': formation,
        'inscription_reussie': inscription_reussie
    })