from __future__ import annotations

import json
import os.path
from typing import Optional

from django.contrib import messages
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView

from authentication.mixins import LoginRequiredMixin
from backend.DatasetInfo import DatasetInfo
from experiments.forms.create import DatasetUploadForm
from experiments.forms.edit import DatasetEditForm
from experiments.models.dataset import Dataset, CleaningState
from experiments.models.managers import DatasetQuerySet
from experiments.services.dataset import (
    save_dataset,
    get_download_response,
)
from experiments.services.dataset import schedule_backend
from experiments.views.generic import PostOnlyDeleteView


class DatasetUploadView(LoginRequiredMixin, CreateView[Dataset, DatasetUploadForm]):
    model = Dataset
    form_class = DatasetUploadForm
    template_name = "dataset_upload.html"
    success_url = reverse_lazy("dataset_overview")

    # Overwrite post to find error in dataset uploads
    def post(self, request, *args, **kwargs):
        form = self.get_form()

        # Check is form is invalid and set error messages
        if not form.is_valid():
            error_text = " ".join(
                [
                    error_message
                    for error in form.errors.values()
                    for error_message in error
                ]
            )

            messages.error(request, f"Invalid dataset: {error_text}")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # save the file temporarily to disk
        temp_file_path: str = save_dataset(self.request.FILES["path_original"])
        assert os.path.isfile(temp_file_path)

        try:
            dataset_valid = DatasetInfo.is_dataset_valid(temp_file_path)
        except UnicodeError as e:
            os.remove(temp_file_path)
            messages.error(
                self.request, "Unicode error in selected dataset: " + e.reason
            )
            assert not os.path.isfile(temp_file_path)
            return super(DatasetUploadView, self).form_invalid(form)

        # check if the file is a csv file
        if not dataset_valid:
            os.remove(temp_file_path)

            # TODO: Maybe an error in FileField validator?
            # return an error
            form.add_error("path_original", "The given file is not a valid csv.-file.")
            assert not os.path.isfile(temp_file_path)
            return super(DatasetUploadView, self).form_invalid(form)

        # don't add the data on datapoints and dimensions to the model

        os.remove(temp_file_path)

        form.instance.user = self.request.user
        form.instance.status = CleaningState.RUNNING.name

        # call the super().form_valid() before creating the DatasetCleaning, as the primary key is needed
        # to create the DatasetCleaning
        response = super(DatasetUploadView, self).form_valid(form)
        assert form.instance.pk is not None

        # start Dataset Cleaning
        schedule_backend(form.instance)

        assert not os.path.isfile(temp_file_path)

        return response


class DatasetOverview(LoginRequiredMixin, ListView[Dataset]):
    model = Dataset
    template_name = "dataset_overview.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        datasets: DatasetQuerySet = Dataset.objects.get_by_user(self.request.user)

        # Sorting
        sort_by: str = self.kwargs["sort"]
        if sort_by == "upload_date":
            datasets = datasets.get_sorted_by_upload_time()
        else:
            datasets = datasets.get_sorted_by_name()

        context.update({"models_list": datasets})
        return context


class DatasetDeleteView(LoginRequiredMixin, PostOnlyDeleteView[Dataset]):
    model = Dataset
    success_url = reverse_lazy("dataset_overview")

    def form_valid(self, form) -> HttpResponse:
        # processing before object is deleted
        # access object and its fields
        dataset: Dataset = self.get_object()

        # find experiment via related name in models of experiment
        if not dataset.is_deletable:
            # return reverse_lazy("dataset_overview")
            return HttpResponseRedirect(reverse_lazy("dataset_overview"))
        return super().form_valid(form)


class DatasetEditView(LoginRequiredMixin, UpdateView[Dataset, DatasetEditForm]):
    model = Dataset
    form_class = DatasetEditForm
    template_name = "dataset_edit.html"
    success_url = reverse_lazy("dataset_overview")


def download_uncleaned_dataset(
    request: HttpRequest, pk: int
) -> Optional[HttpResponse | HttpResponseRedirect]:
    if request.method == "GET":
        dataset: Optional[Dataset] = Dataset.objects.filter(pk=pk).first()
        if dataset is None:
            if "admin" not in request.path:
                return HttpResponseRedirect(reverse_lazy("dataset_overview"))
            return HttpResponseRedirect(
                reverse_lazy("admin:experiments_dataset_changelist")
            )

        with dataset.path_original as file:
            return get_download_response(file, f"{dataset.display_name}.csv")
    return None


def download_cleaned_dataset(
    request: HttpRequest, pk: int
) -> Optional[HttpResponse | HttpResponseRedirect]:
    if request.method == "GET":
        dataset: Optional[Dataset] = Dataset.objects.filter(pk=pk).first()
        if dataset is None or dataset.is_cleaned is False:
            if "admin" not in request.path:
                return HttpResponseRedirect(reverse_lazy("dataset_overview"))
            return HttpResponseRedirect(
                reverse_lazy("admin:experiments_dataset_changelist")
            )

        with dataset.path_cleaned as file:
            return get_download_response(file, f"{dataset.display_name}_cleaned.csv")
    return None


def dataset_status_view(
    request: HttpRequest,
) -> Optional[HttpResponse | HttpResponseRedirect]:
    if request.method == "GET":
        dataset_pk: int = -1
        if "dataset_pk" in request.GET:
            dataset_pk = int(request.GET["dataset_pk"])
        elif "dataset_pk" in request.META:
            dataset_pk = request.META["dataset_pk"]
        if dataset_pk >= 0:
            dataset: Optional[Dataset] = Dataset.objects.filter(pk=dataset_pk).first()
            if dataset is None:
                return HttpResponseRedirect(reverse_lazy("dataset_overview"))

            data = {"dataset_pk": dataset.pk, "is_cleaned": dataset.is_cleaned}
            return HttpResponse(json.dumps(data))
    return None
