from django.contrib import admin
from .models import Edition, ImagesEdition


class ImagesEditionInline(admin.TabularInline):
    model = ImagesEdition
    extra = 3


@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    list_display = ("annee",)
    search_fields = ("annee",)
    ordering = ("-annee",)
    inlines = [ImagesEditionInline]


@admin.register(ImagesEdition)
class ImagesEditionAdmin(admin.ModelAdmin):
    list_display = ("edition", "image")
    list_filter = ("edition",)
    search_fields = ("edition__annee",)