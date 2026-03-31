from django.views.generic import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import ReservationWorkspaceForm

class WorkspaceReservationView(FormView):
    template_name = "Workspace/workspace.html"
    form_class = ReservationWorkspaceForm
    success_url = reverse_lazy("workspace")  # ou ton url name

    PRIX_HEURE = 0.5

    def form_valid(self, form):
        form.save()
        # Flag de succès pour le template
        self.request.session["reservation_reussie"] = True
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print(form.errors)  # Affiche les erreurs dans la console
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prix_heure"] = self.PRIX_HEURE
        # Récupérer le flag et le supprimer de la session
        context["reservation_reussie"] = self.request.session.pop(
            "reservation_reussie", False
        )
        return context
