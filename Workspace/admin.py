from django.contrib import admin

from .models import ConfigurationWorkspace, ReservationWorkspace


@admin.register(ConfigurationWorkspace)
class ConfigurationWorkspaceAdmin(admin.ModelAdmin):
    list_display = ("__str__", "reservations_ouvertes")

    def has_add_permission(self, request):
        return not ConfigurationWorkspace.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


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
