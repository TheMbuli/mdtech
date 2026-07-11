from django.views.generic import DetailView
from django.views.generic.list import ListView

from .models import Article


class Boutique(ListView):
    model = Article
    template_name = "Boutique/boutique.html"
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.prefetch_related("photos")


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'Boutique/details_article.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Article.objects.prefetch_related("photos")
