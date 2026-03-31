from django.urls import path
from . import views

urlpatterns = [
    path('', views.projets_list, name='projets-list'),
    path('<int:projet_id>/', views.projet_detail, name='details-projet'),
]
