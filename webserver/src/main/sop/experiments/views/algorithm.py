import os
import random
import string
from typing import Optional

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    DeleteView,
    UpdateView,
    DetailView,
)

from authentication.mixins import LoginRequiredMixin
from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from experiments.forms.create import AlgorithmUploadForm
from experiments.forms.edit import AlgorithmEditForm
from experiments.models import Algorithm
from sop.settings import MEDIA_ROOT


class AlgorithmOverview(LoginRequiredMixin, ListView):
    model = Algorithm
    template_name = "algorithm_overview.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get sort by variable and get sorted set
        sort_by = self.kwargs["sort"]
        if sort_by == "group":
            sorted_list = Algorithm.objects.get_sorted_by_group_and_name()
        elif sort_by == "upload_date":
            sorted_list = Algorithm.objects.get_sorted_by_upload_date()
        else:
            sorted_list = Algorithm.objects.get_sorted_by_name()

        # Filter algorithms to only show own and public algorithms
        sorted_list = sorted_list.get_by_user_and_public(self.request.user)

        context.update({"models_list": sorted_list})
        return context


def get_signature_of_algorithm(path: str) -> str:
    algorithm_parameters = AlgorithmLoader.get_algorithm_parameters(path)
    keys_values = algorithm_parameters.items()
    string_dict = {key: str(value) for key, value in keys_values}
    return ",".join(string_dict.values())


class AlgorithmUploadView(LoginRequiredMixin, CreateView):
    model = Algorithm
    form_class = AlgorithmUploadForm
    template_name = "algorithm_upload.html"
    success_url = reverse_lazy("algorithm_overview")

    def form_valid(self, form) -> HttpResponse:
        temp_path: str = self.request.FILES["path"].temporary_file_path()

        error: Optional[str] = AlgorithmLoader.is_algorithm_valid(temp_path)

        if error is not None:
            # add the error to the form and display it as invalid
            form.errors.update({"path": [error]})
            return super(AlgorithmUploadView, self).form_invalid(form)

        elif error is None:
            form.instance.user = self.request.user
            form.instance.signature = get_signature_of_algorithm(temp_path)
            return super(AlgorithmUploadView, self).form_valid(form)


class AlgorithmDeleteView(LoginRequiredMixin, DeleteView):
    model = Algorithm
    template_name = "algorithm_delete.html"
    success_url = reverse_lazy("algorithm_overview")


class AlgorithmEditView(LoginRequiredMixin, UpdateView):
    model = Algorithm
    form_class = AlgorithmEditForm
    template_name = "algorithm_edit.html"
    success_url = reverse_lazy("algorithm_overview")


class AlgorithmDetailView(LoginRequiredMixin, DetailView):
    model = Algorithm
    # TODO: template?
    # template_name =
