from django.urls import path
from .views import (Boutique, ArticleDetailView)

urlpatterns = [
    path('',Boutique.as_view(), name='boutique'),
    path('<int:pk>/', ArticleDetailView.as_view(),name='details-article')
]
