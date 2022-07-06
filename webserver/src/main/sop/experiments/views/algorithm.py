import os
import random
import string
from typing import Optional

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
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
        sorted_by_group = Algorithm.objects.get_sorted_by_group_and_name()
        sorted_by_group = sorted_by_group.filter(
            Q(user_id__exact=self.request.user.id) | Q(user_id__exact=None)
        )
        context.update({"models_list": sorted_by_group})
        return context


def save_temporary_algorithm(file: InMemoryUploadedFile) -> str:
    # create temp_path
    temp_dir = MEDIA_ROOT / "algorithms/temp"
    temp_file_path = temp_dir / "".join(
        random.choice(string.ascii_lowercase) for i in range(10)
    )

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # save contents of uploaded file into temp file
    with open(temp_file_path, "wb") as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)

    return str(temp_file_path)


def delete_temporary_algorithm(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        print("Couldn't delete file")


class AlgorithmUploadView(LoginRequiredMixin, CreateView):
    model = Algorithm
    form_class = AlgorithmUploadForm
    template_name = "algorithm_upload.html"
    success_url = reverse_lazy("algorithm_overview")

    def form_valid(self, form) -> HttpResponse:
        form.instance.user = self.request.user
        file: InMemoryUploadedFile = self.request.FILES["path"]

        # save the contents of the uploaded file in a temporary file and check
        # it for a valid implementation of BaseDetector
        temp_path: str = save_temporary_algorithm(file)
        error: Optional[str] = AlgorithmLoader.is_algorithm_valid(temp_path)
        delete_temporary_algorithm(temp_path)

        if error is not None:
            # add the error to the form and display it as invalid
            form.errors.update({"path": [error]})
            return super(AlgorithmUploadView, self).form_invalid(form)

        elif error is None:
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
