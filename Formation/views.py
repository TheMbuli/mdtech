from django.views.generic.list import ListView
from django.views.generic import DetailView
from .models import Formation
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .forms import InscriptionForm
from .models import Inscription
# Create your views here

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
        # On définit l'instance formation avant validation
        form.instance.formation = formation
        if Inscription.objects.filter(email=form.data.get('email'), formation=formation).exists():
            form.add_error('email', "Vous êtes déjà inscrit à cette formation avec cet email.")
        elif form.is_valid():
            form.save()
            inscription_reussie = True
    else:
        form = InscriptionForm()

    return render(request, 'Formation/inscription.html', {
        'form': form,
        'formation': formation,
        'inscription_reussie': inscription_reussie
    })
