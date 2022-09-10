from __future__ import annotations

import json
import os.path
from typing import Optional

from django.contrib import messages
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from authentication.mixins import LoginRequiredMixin
from backend.DatasetInfo import DatasetInfo
from experiments.forms.create import DatasetUploadForm
from experiments.forms.edit import DatasetEditForm
from experiments.mixins import SingleObjectPermissionMixin
from experiments.models.dataset import Dataset, CleaningState
from experiments.models.managers import DatasetQuerySet
from experiments.services.dataset import (
    save_dataset,
    get_download_response,
)
from experiments.services.dataset import schedule_backend
from experiments.views.generic import PostOnlyDeleteView


class DatasetUploadView(LoginRequiredMixin, CreateView[Dataset, DatasetUploadForm]):
    """
    A view to upload a dataset. It will use the DatasetUploadForm to display widgets for
    the fields that a user has to enter. When the form is valid, this view will save the
    dataset in the database and start a DatasetCleaning for the given dataset.
    """

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

        dataset_valid = DatasetInfo.is_dataset_valid(temp_file_path)

        os.remove(temp_file_path)

        if not dataset_valid:
            messages.error(
                self.request, "Error in selected dataset, dataset is invalid."
            )
            return super(DatasetUploadView, self).form_invalid(form)

        form.instance.user = self.request.user
        form.instance.status = CleaningState.RUNNING.name

        # call the super().form_valid() before creating the DatasetCleaning,
        # as the primary key is needed to create the DatasetCleaning
        response = super(DatasetUploadView, self).form_valid(form)
        assert form.instance.pk is not None

        # start Dataset Cleaning
        schedule_backend(form.instance)

        return response


class DatasetOverview(LoginRequiredMixin, ListView[Dataset]):
    """
    A view to display all datasets of the user that requests this view. Datasets can
    be sorted by traits like name and upload date.
    """

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


class DatasetDeleteView(
    LoginRequiredMixin, SingleObjectPermissionMixin, PostOnlyDeleteView[Dataset]
):
    """
    A view to delete a dataset. It inherits PostOnlyDeleteView, so it is only accessible
    via a POST request and will then perform the deletion of the dataset model.
    """

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


class DatasetEditView(
    LoginRequiredMixin,
    SingleObjectPermissionMixin,
    UpdateView[Dataset, DatasetEditForm],
):
    """
    A view to edit an existing dataset. It uses the DatasetEditForm to display widgets
    for fields that a user can edit.
    """

    model = Dataset
    form_class = DatasetEditForm
    template_name = "dataset_edit.html"
    success_url = reverse_lazy("dataset_overview")


def download_uncleaned_dataset(
    request: HttpRequest, pk: int
) -> Optional[HttpResponse | HttpResponseRedirect]:
    """
    A function view to download the uncleaned csv of a dataset.
    @param request: The HTTPRequest, this will be given by django.
    @param pk: The primary key of the wanted dataset.
    @return: If the request is correct and a dataset with the given primary key exists,
    this view will return a HTTPResponse with the download. If there is no dataset with
    the given primary key, the view will redirect to the dataset overview.
    If this view is accessed via a POST request it will return None.
    """
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
    """
    A function view to download the cleaned csv of a dataset. This view asserts that the
    dataset is already cleaned. Calling this view with an uncleaned dataset will result
    in unexpected behaviour.
    @param request: The HTTPRequest, this will be given by django.
    @param pk: The primary key of the wanted dataset.
    @return: If the request is correct and a dataset with the given primary key exists,
    this view will return a HTTPResponse with the download. If there is no dataset with
    the given primary key, the view will redirect to the dataset overview.
    If this view is accessed via a POST request it will return None.
    """
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
    """
    A function view to retrieve the status of a dataset and it's cleaning progress.
    It is used in dataset templates to display this information to a user.
    @param request: The HttpRequest, given by django. It must contain the datasets
    primary key in it.
    @return: A HttpResponse containing JSON data describing the status and progress
    of the wanted dataset, if a dataset with the given primary key exists.
    If no dataset with the given primary exists, this redirects to the dataset overview.
    If this view is accessed via a POST request or no primary key is given,
    it will return None.
    """
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

            data = {
                "dataset_pk": dataset.pk,
                "cleaning_status": dataset.status,
                "progress": dataset.cleaning_progress,
            }
            return HttpResponse(json.dumps(data))
    return None
