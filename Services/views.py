from django.shortcuts import render
from .models import Service


def services(request):
    data = Service.objects.all()

    return render(request, 'Services/services.html', {
        "services": data
    })
