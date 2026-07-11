from django.shortcuts import render
from .models import Edition


def gallery_view(request):
    editions = Edition.objects.prefetch_related("images")

    return render(request, "Gallery/gallery-list.html", {
        "editions": editions
    })
