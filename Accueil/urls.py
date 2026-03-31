from django.urls import path
from .views import (Accueil)
urlpatterns = [
    path('',Accueil.as_view(),name='accueil')
]
