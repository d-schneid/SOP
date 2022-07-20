import json
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView,
)

from authentication.mixins import LoginRequiredMixin
from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from experiments.forms.create import AlgorithmUploadForm
from experiments.forms.edit import AlgorithmEditForm
from experiments.models import Algorithm
from experiments.services.algorithm import (
    save_temp_algorithm,
    delete_temp_algorithm,
    convert_param_mapping_to_signature_dict,
)
from experiments.views.generic import PostOnlyDeleteView

ALGORITHM_ROOT_DIR = settings.MEDIA_ROOT / "algorithms"


class AlgorithmOverview(LoginRequiredMixin, ListView[Algorithm]):
    model = Algorithm
    template_name = "algorithm_overview.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        sorted_list = Algorithm.objects.get_by_user(self.request.user)
        # Get sort by variable and get sorted set
        sort_by = self.kwargs["sort"]
        if sort_by == "group":
            sorted_list = sorted_list.get_sorted_by_group_and_name()
        elif sort_by == "upload_date":
            sorted_list = sorted_list.get_sorted_by_upload_date()
        else:
            sorted_list = sorted_list.get_sorted_by_name()

        context.update({"models_list": sorted_list})
        return context


class AlgorithmUploadView(
    LoginRequiredMixin, CreateView[Algorithm, AlgorithmUploadForm]
):
    model = Algorithm
    form_class = AlgorithmUploadForm
    template_name = "algorithm_upload.html"
    success_url = reverse_lazy("algorithm_overview")

    def form_valid(self, form) -> HttpResponse:
        file: InMemoryUploadedFile = self.request.FILES["path"]  # type: ignore

        temp_path: Path = save_temp_algorithm(self.request.user, file)
        AlgorithmLoader.set_algorithm_root_dir(str(ALGORITHM_ROOT_DIR))
        AlgorithmLoader.ensure_root_dir_in_path()
        error: Optional[str] = AlgorithmLoader.is_algorithm_valid(str(temp_path))
        if error is None:
            mapping = AlgorithmLoader.get_algorithm_parameters(str(temp_path))
            dikt = convert_param_mapping_to_signature_dict(mapping)
            form.instance.signature = json.dumps(dikt)
        delete_temp_algorithm(temp_path)

        if error is not None:
            # add the error to the form and display it as invalid
            form.errors.update({"path": [error]})
            return super(AlgorithmUploadView, self).form_invalid(form)

        elif error is None:
            form.instance.user = self.request.user
            return super(AlgorithmUploadView, self).form_valid(form)


class AlgorithmDeleteView(LoginRequiredMixin, PostOnlyDeleteView[Algorithm]):
    model = Algorithm
    success_url = reverse_lazy("algorithm_overview")


class AlgorithmEditView(LoginRequiredMixin, UpdateView[Algorithm, AlgorithmEditForm]):
    model = Algorithm
    form_class = AlgorithmEditForm
    template_name = "algorithm_edit.html"
    success_url = reverse_lazy("algorithm_overview")


class AlgorithmDetailView(LoginRequiredMixin, DetailView[Algorithm]):
    model = Algorithm
    # TODO: template?
    # template_name =
