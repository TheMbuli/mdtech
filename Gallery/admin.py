from django.contrib import admin
from .models import Gallery, Image

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = ('titre', 'date_creation')
