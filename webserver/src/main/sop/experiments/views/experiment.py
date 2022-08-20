from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Any

from django.contrib import messages
from django.db import models
from django.http import HttpResponse, HttpRequest
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from authentication.mixins import LoginRequiredMixin
from experiments.forms.create import ExperimentCreateForm
from experiments.forms.edit import ExperimentEditForm
from experiments.models import Experiment, Dataset, Execution
from experiments.models.algorithm import Algorithm
from experiments.models.managers import ExperimentQuerySet
from experiments.services.execution import get_download_http_response
from experiments.views.generic import PostOnlyDeleteView


class ExperimentOverview(LoginRequiredMixin, ListView[Experiment]):
    """
    A view to display all experiments of a user. Experiments can be sorted by traits
    like their display name or creation date
    """
    model = Experiment
    template_name = "experiment_overview.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
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
    """
    A view to create a new experiment. It uses the ExperimentCreateForm to display
    widgets for the fields needed to create a new experiment.
    When the form inputs are valid it will create the experiment model and save it in
    the database.
    """
    model = Experiment
    template_name = "experiment_create.html"
    form_class = ExperimentCreateForm
    success_url = reverse_lazy("experiment_overview")

    def form_valid(self, form: ExperimentCreateForm) -> HttpResponse:
        form.instance.user = self.request.user

        # get algorithms
        algos: list[Algorithm] = [
            Algorithm.objects.get(pk=key)
            for key in self.request.POST.getlist("check-algo")
        ]

        # If no algos are selected, display error
        if len(algos) == 0:
            messages.error(self.request, "Please select at least one algorithm!")
            return super().form_invalid(form)

        response: HttpResponse = super().form_valid(form)

        # Add algorithms to experiment
        for algo in algos:
            form.instance.algorithms.add(algo)

        form.instance.save()

        return response

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"].fields["dataset"].queryset = Dataset.objects.get_by_user(
            self.request.user
        ).filter(status="FINISHED")
        # Add algorithm groups,
        # algorithms and datasets to context here, to be able to generate and customize
        # non-django html forms
        context.update(
            {
                "algorithm_groups": Algorithm.AlgorithmGroup,
                "algorithms": Algorithm.objects.get_by_user_and_public(
                    self.request.user
                ),
                "datasets": Dataset.objects.get_by_user(self.request.user),
            }
        )
        return context


class ExperimentDuplicateView(ExperimentCreateView):
    """
    A view to duplicate an experiment. It inherits from ExperimentCreateView and
    therefor will behave the same way, except that it provides default values for the
    needed fields that match the original experiments values.
    """

    def get_initial(
            self,
    ) -> dict[str, Any]:
        form: dict[str, Any] = {}
        if self.request.method == "GET":
            og_experiment_pk = self.kwargs["pk"]
            original = Experiment.objects.get(pk=og_experiment_pk)
            form["display_name"] = original.display_name
            form["dataset"] = original.dataset
        return form

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        og_experiment_pk = self.kwargs["pk"]
        original = Experiment.objects.get(pk=og_experiment_pk)
        context.update({"initial_algorithms": original.algorithms.all()})
        return context


class ExperimentEditView(
    LoginRequiredMixin, UpdateView[Experiment, ExperimentEditForm]
):
    """
    A view to edit an existing experiment. It uses the ExperimentEditForm to display
    widgets for the fields a user can edit.
    """
    model = Experiment
    form_class = ExperimentEditForm
    template_name = "experiment_edit.html"
    success_url = reverse_lazy("experiment_overview")


class ExperimentDeleteView(LoginRequiredMixin, PostOnlyDeleteView[Experiment]):
    """
    A view to delete an existing experiment. It inherits from PostOnlyDeleteView and
    can therefor only be accessed with a POST request.
    """
    model = Experiment
    success_url = reverse_lazy("experiment_overview")


def download_all_execution_results(request: HttpRequest, pk: int):
    if not Experiment.objects.filter(pk=pk).exists():
        return

    if request.method == "GET":
        experiment = Experiment.objects.get(pk=pk)
        executions: models.QuerySet[Execution] = Execution.objects.filter(
            experiment=experiment
        )

        # create zip file in memory
        in_memory_file = io.BytesIO()
        with zipfile.ZipFile(in_memory_file, "a") as zip_file:
            # save all results of finished executions in our zip file
            for execution in executions:
                if execution.has_result:
                    with execution.result_path as file:
                        result_name = Path(file.path).name
                        zip_file.writestr(result_name, file.read())
        # zip file is closed, we can send the data of it to the user
        return get_download_http_response(
            in_memory_file.getvalue(), f"{experiment.display_name}_results.zip"
        )
    return None
