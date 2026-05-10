from django.shortcuts import render
from .models import Service
import requests
import os
from dotenv import load_dotenv

load_dotenv()

IP_API_KEY = os.getenv("IP_API_KEY")
IS_DEV = os.getenv("DEV","True").lower() == "true"


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    print("---------------------"+request.META.get('REMOTE_ADDR'))
    return request.META.get('REMOTE_ADDR')


def get_geolocation(ip):
    try:
        response = requests.get(
            f"https://ipfind.co/?auth={IP_API_KEY}&ip={ip}",
            timeout=5
        )
        data = response.json()
        return data
    except Exception as e:
        print("Erreur géolocation:", e)
        return None


def services(request):
    data = Service.objects.all()

    ip_address = get_client_ip(request)
    if not request.session.get("geo"):
        if IS_DEV:
            request.session["geo"] = {
                "city": "Goma",
                "country": "DRC",
                "ip": "127.0.0.1"
            }
        else:
            request.session["geo"] = get_geolocation(ip_address)

    geo_data = request.session.get("geo")

    return render(request, 'Services/services.html', {
        "services": data,
        "geo": geo_data
    })
