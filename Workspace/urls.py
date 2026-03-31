from django.urls import path
from .views import (WorkspaceReservationView)
urlpatterns = [
    path('',WorkspaceReservationView.as_view(),name='workspace'),
]
