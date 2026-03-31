from django.contrib import admin
from .models import Projet, PhotoProjet


class PhotoProjetInline(admin.TabularInline):
    model = PhotoProjet
    extra = 1


@admin.register(Projet)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [PhotoProjetInline]