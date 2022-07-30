from __future__ import annotations

from typing import Any, Dict, List

from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from authentication.mixins import LoginRequiredMixin
from experiments.forms.create import ExperimentCreateForm
from experiments.forms.edit import ExperimentEditForm
from experiments.models import Experiment, Dataset
from experiments.models.managers import ExperimentQuerySet
from experiments.views.generic import PostOnlyDeleteView
from experiments.models.algorithm import Algorithm


class ExperimentOverview(LoginRequiredMixin, ListView[Experiment]):
    model = Experiment
    template_name = "experiment_overview.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
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
    form_class = ExperimentCreateForm
    success_url = reverse_lazy("experiment_overview")

    def form_valid(self, form: ExperimentCreateForm) -> HttpResponse:
        form.instance.user = self.request.user

        # get algorithms
        algos: List[Algorithm] = [Algorithm.objects.get(pk=key) for key in self.request.POST.getlist("check-algo")]

        # If no algos are selected, display error
        if len(algos) == 0:
            messages.error(self.request, f"Please select at least one algorithm!")
            return super().form_invalid(form)

        response: HttpResponse = super().form_valid(form)

        # Add algorithms to experiment
        for algo in algos:
            form.instance.algorithms.add(algo)

        form.instance.save()

        return response

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            "algorithm_groups": Algorithm.AlgorithmGroup,
            "algorithms": Algorithm.objects.get_by_user_and_public(self.request.user),
        })
        return context

    def get_form(self, *args: Any, **kwargs: Any) -> ExperimentCreateForm:
        form = super().get_form(*args, **kwargs)
        form.fields["dataset"].queryset = Dataset.objects.\
            get_by_user(self.request.user).\
            filter(is_cleaned=True)
        return form


class ExperimentDuplicateView(ExperimentCreateView):
    def get_initial(
        self,
    ) -> Dict[str, Any]:
        form: Dict[str, Any] = {}
        if self.request.method == "GET":
            og_experiment_pk = self.kwargs["pk"]
            original = Experiment.objects.get(pk=og_experiment_pk)
            form["display_name"] = original.display_name
            form["dataset"] = original.dataset
            form["algorithms"] = original.algorithms.all()
        return form


class ExperimentEditView(
    LoginRequiredMixin, UpdateView[Experiment, ExperimentEditForm]
):
    model = Experiment
    form_class = ExperimentEditForm
    template_name = "experiment_edit.html"
    success_url = reverse_lazy("experiment_overview")


class ExperimentDeleteView(LoginRequiredMixin, PostOnlyDeleteView[Experiment]):
    model = Experiment
    template_name = "experiment_delete.html"
    success_url = reverse_lazy("experiment_overview")
