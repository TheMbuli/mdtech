from django.shortcuts import render
from django.views import View
from Realisations.models import Projet

class Accueil(View):
    template = "Accueil/accueil.html"

    def get(self, request):
        projets_recents = Projet.objects.prefetch_related("photos")[:3]
        return render(request, self.template, {'projets_recents': projets_recents})
