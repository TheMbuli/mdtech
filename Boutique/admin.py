from django.contrib import admin
from .models import Article, PhotoArticle


class PhotoArticleInline(admin.TabularInline):
    model = PhotoArticle
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [PhotoArticleInline]
