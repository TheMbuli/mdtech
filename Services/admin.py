from django.contrib import admin
from .models import Service, PhotoService

# Register your models here.
class PhotoServiceInline(admin.TabularInline):
    model = PhotoService
    extra = 5


@admin.register(Service)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [PhotoServiceInline]