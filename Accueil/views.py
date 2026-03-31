from django.shortcuts import render
from django.views import View
from Realisations.models import Projet

class Accueil(View):
    template = "Accueil/accueil.html"

    def get(self, request):
        projets_recents = Projet.objects.order_by('-date_creation')[:3]  # par ex. 3 projets récents
        return render(request, self.template, {'projets_recents': projets_recents})
