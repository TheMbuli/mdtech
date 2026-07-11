from django.shortcuts import render, get_object_or_404
from .models import Projet

def projets_list(request):
    projets = Projet.objects.prefetch_related("photos")
    return render(request, 'Projects/projects.html', {'projets': projets})

def projet_detail(request, projet_id):
    projet = get_object_or_404(Projet.objects.prefetch_related("photos"), id=projet_id)
    photos = projet.photos.all()
    return render(request, 'Projects/details-projet.html', {'projet': projet, 'photos': photos})
