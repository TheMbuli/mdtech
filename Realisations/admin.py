from django.contrib import admin
from .models import Projet, PhotoProjet


class PhotoProjetInline(admin.TabularInline):
    model = PhotoProjet
    extra = 1


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    inlines = [PhotoProjetInline]
    list_display = ("titre", "date_creation")
    search_fields = ("titre", "description")
    ordering = ("-date_creation",)
    readonly_fields = ("date_creation",)
    date_hierarchy = "date_creation"
