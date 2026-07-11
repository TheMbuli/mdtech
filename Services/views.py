from django.shortcuts import render
from .models import Service


def services(request):
    data = Service.objects.prefetch_related("images")

    return render(request, 'Services/services.html', {
        "services": data
    })
