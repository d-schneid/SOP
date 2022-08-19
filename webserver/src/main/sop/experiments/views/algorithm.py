from __future__ import annotations

from pathlib import Path
from typing import Optional, Any

from django.contrib import messages
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpRequest, HttpResponseRedirect
from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
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
from experiments.services.dataset import get_download_response
from experiments.views.generic import PostOnlyDeleteView


class AlgorithmOverview(LoginRequiredMixin, ListView[Algorithm]):
    """
    A view to display all algorithms of a user, optionally sorted by specific traits
    like name, group or upload_date.
    """
    model = Algorithm
    template_name = "algorithm_overview.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        sorted_list = Algorithm.objects.get_by_user(self.request.user)  # type: ignore
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
    """
    A view to upload an own algorithm. It will check the algorithm for validity before
    saving the algorithm in the database to make it usable for experiment creation
    later.
    """
    model = Algorithm
    form_class = AlgorithmUploadForm
    template_name = "algorithm_upload.html"
    success_url = reverse_lazy("algorithm_overview")

    def form_valid(self, form: AlgorithmUploadForm) -> HttpResponse:
        file: InMemoryUploadedFile = self.request.FILES["path"]  # type: ignore

        temp_path: Path = save_temp_algorithm(self.request.user, file)
        error: Optional[str] = AlgorithmLoader.is_algorithm_valid(str(temp_path))
        if error is None:
            mapping = AlgorithmLoader.get_algorithm_parameters(str(temp_path))
            dikt = convert_param_mapping_to_signature_dict(mapping)
            form.instance.signature = dikt
        delete_temp_algorithm(temp_path)

        if error is not None:
            # add the error to the form and display it as invalid
            messages.error(self.request, f"Algorithm invalid: {error}")
            return super(AlgorithmUploadView, self).form_invalid(form)

        elif error is None:
            form.instance.user = self.request.user
            return super(AlgorithmUploadView, self).form_valid(form)


class AlgorithmDeleteView(LoginRequiredMixin, PostOnlyDeleteView[Algorithm]):
    """
    A view to delete an algorithm. It inherits from PostOnlyDeleteView, so it can only
    be called via a POST request and then execute the deletion.
    """
    model = Algorithm
    success_url = reverse_lazy("algorithm_overview")


class AlgorithmEditView(LoginRequiredMixin, UpdateView[Algorithm, AlgorithmEditForm]):
    """
    A view to edit an existing algorithm. It uses the AlgorithmEditForm to display
    widgets for the fields that a user can edit.
    """
    model = Algorithm
    form_class = AlgorithmEditForm
    template_name = "algorithm_edit.html"
    success_url = reverse_lazy("algorithm_overview")


def download_algorithm(
        request: HttpRequest, pk: int
) -> Optional[HttpResponse | HttpResponseRedirect]:
    """
    A function view that will let the user download a algorithm.
    @param request: The HTTPRequest, this will be given by django.
    @param pk: The primary key of the algorithm that will be downloaded.
    @return: If the request is successful and an algorithm with the given primary
    key exists, this function will return a HTTPResponse with the download of the
    algorithm. Otherwise, it will return a redirect to the algorithm overview.
    If this function is accessed with a POST request, it will return None.
    """
    if request.method == "GET":
        algorithm: Optional[Algorithm] = Algorithm.objects.filter(pk=pk).first()
        if algorithm is None:
            if "admin" not in request.path:
                return HttpResponseRedirect(reverse_lazy("algorithm_overview"))
            return HttpResponseRedirect(
                reverse_lazy("admin:experiments_algorithm_changelist"))

        with algorithm.path as file:
            return get_download_response(file, f"{algorithm.display_name}.py")
    return None
