from django.shortcuts import render, get_object_or_404
from .models import Projet

# Liste des projets
def projets_list(request):
    projets = Projet.objects.all().order_by('-date_creation')
    return render(request, 'Projects/projects.html', {'projets': projets})

# Détails d'un projet
def projet_detail(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)
    photos = projet.photos.all()  # récupère toutes les photos liées
    return render(request, 'Projects/details-projet.html', {'projet': projet, 'photos': photos})
