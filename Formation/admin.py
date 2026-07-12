from django.contrib import admin

from .models import Formation, Inscription


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = (
        "nom",
        "inscriptions_ouvertes",
        "duree",
        "prix_pro",
        "prix_etudiant",
        "updated_at",
    )
    list_editable = ("inscriptions_ouvertes",)
    list_filter = ("inscriptions_ouvertes",)
    search_fields = ("nom", "description", "objectifs")
    ordering = ("nom",)
    prepopulated_fields = {"slug": ("nom",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "formation", "email", "date_inscription")
    list_filter = ("formation", "date_inscription")
    search_fields = ("nom", "prenom", "email", "telephone", "formation__nom")
    ordering = ("-date_inscription",)
    readonly_fields = ("date_inscription",)
    date_hierarchy = "date_inscription"
    list_select_related = ("formation",)
