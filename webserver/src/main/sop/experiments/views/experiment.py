from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from authentication.mixins import LoginRequiredMixin
from experiments.forms.create import ExperimentCreateForm
from experiments.forms.edit import ExperimentEditForm
from experiments.models import Experiment
from experiments.models.managers import ExperimentQuerySet


class ExperimentOverview(LoginRequiredMixin, ListView[Experiment]):
    model = Experiment
    template_name = "experiment_overview.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        experiments: ExperimentQuerySet = Experiment.objects.get_by_user(
            self.request.user
        )

        # Sorting
        sort_by: str = self.kwargs["sort"]
        if sort_by == "creation_date":
            experiments = experiments.get_sorted_by_creation_date()
        else:
            experiments = experiments.get_sorted_by_name()

        context.update({"models_list": experiments})
        return context


class ExperimentCreateView(
    LoginRequiredMixin, CreateView[Experiment, ExperimentCreateForm]
):
    model = Experiment
    template_name = "experiment_create.html"
    # TODO: use ExperimentCreateForm
    fields = ("display_name", "dataset", "algorithms")
    success_url = reverse_lazy("experiment_overview")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ExperimentCreateView, self).form_valid(form)


class ExperimentEditView(
    LoginRequiredMixin, UpdateView[Experiment, ExperimentEditForm]
):
    model = Experiment
    form_class = ExperimentEditForm
    template_name = "experiment_edit.html"
    success_url = reverse_lazy("experiment_overview")


class ExperimentDeleteView(LoginRequiredMixin, DeleteView[Experiment]):
    model = Experiment
    template_name = "experiment_delete.html"
    success_url = reverse_lazy("experiment_overview")
