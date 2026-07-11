from django.contrib import admin
from .models import Service, PhotoService

class PhotoServiceInline(admin.TabularInline):
    model = PhotoService
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    inlines = [PhotoServiceInline]
    list_display = ("nom", "pricing")
    search_fields = ("nom", "description", "pricing")
    ordering = ("nom",)
