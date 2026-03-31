from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic import DetailView
from .models import Article

class Boutique(ListView):
    model = Article
    template_name = "Boutique/boutique.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'Boutique/details_article.html'
    context_object_name = 'article'
