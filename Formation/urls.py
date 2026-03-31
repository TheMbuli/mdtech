from django.urls import path
from .views import (FormationListView, FormationDetailView, inscription_view)

urlpatterns = [
    path('',FormationListView.as_view(),name='formation'),
    path('<slug:slug>/', FormationDetailView.as_view(), name='formation_detail'),
    path('<slug:slug>/inscription/', inscription_view, name='formation_inscription'),
]
