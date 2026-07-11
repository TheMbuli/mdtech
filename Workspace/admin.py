from django.contrib import admin

from .models import ReservationWorkspace


@admin.register(ReservationWorkspace)
class ReservationWorkspaceAdmin(admin.ModelAdmin):
    list_display = (
        "nom",
        "date",
        "heure_debut",
        "heure_fin",
        "duree_heures",
        "montant_total",
        "created_at",
    )
    list_filter = ("date", "created_at")
    search_fields = ("nom", "email", "telephone")
    ordering = ("-created_at",)
    readonly_fields = ("duree_heures", "montant_total", "created_at")
    date_hierarchy = "date"
