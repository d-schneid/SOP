from typing import Optional, Any, Dict

import pandas as pd
from django.db.models.fields.files import FieldFile
from django.forms import Form
from django.http import HttpResponse, HttpRequest
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView
from pandas import DataFrame

from authentication.mixins import LoginRequiredMixin
from experiments.forms.create import DatasetUploadForm
from experiments.forms.edit import DatasetEditForm
from experiments.models import Dataset
from experiments.models.managers import DatasetQuerySet
from experiments.views.generic import PostOnlyDeleteView


class DatasetUploadView(LoginRequiredMixin, CreateView[Dataset, DatasetUploadForm]):
    model = Dataset
    form_class = DatasetUploadForm
    template_name = "dataset_upload.html"
    success_url = reverse_lazy("dataset_overview")

    def form_valid(self, form: DatasetUploadForm) -> HttpResponse:
        form.instance.user = self.request.user

        csv_frame: DataFrame = pd.read_csv(
            self.request.FILES["path_original"].temporary_file_path()
        )
        form.instance.datapoints_total = csv_frame.size
        form.instance.dimensions_total = csv_frame.shape[1]

        form.instance.is_cleaned = False
        # TODO: Start Dataset Cleaning

        return super().form_valid(form)


class DatasetOverview(LoginRequiredMixin, ListView[Dataset]):
    model = Dataset
    template_name = "dataset_overview.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
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
    template_name = "dataset_delete.html"
    success_url = reverse_lazy("dataset_overview")

    def form_valid(self, form: Form) -> HttpResponse:
        # processing before object is deleted
        # access object and its fields
        dataset: Dataset = self.get_object()

        # find experiment via related name in models of experiment
        if not dataset.is_deletable:
            # return reverse_lazy("dataset_overview")
            return HttpResponseRedirect(reverse_lazy("dataset_overview"))
        return super(DatasetDeleteView, self).form_valid(form)


class DatasetEditView(LoginRequiredMixin, UpdateView[Dataset, DatasetEditForm]):
    model = Dataset
    form_class = DatasetEditForm
    template_name = "dataset_edit.html"
    success_url = reverse_lazy("dataset_overview")


def get_download_response(file: FieldFile, download_name: str) -> HttpResponse:
    response = HttpResponse(file.read())
    response["Content-Type"] = "text/plain"
    response["Content-Disposition"] = f"attachment; filename={download_name}"
    return response


def download_uncleaned_dataset(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == "GET":
        dataset: Optional[Dataset] = Dataset.objects.filter(pk=pk).first()
        if dataset is None:
            return HttpResponseRedirect(reverse_lazy("dataset_overview"))

        with dataset.path_original as file:
            return get_download_response(file, f"{dataset.display_name}.csv")

    return HttpResponseRedirect(reverse_lazy("dataset_overview"))


def download_cleaned_dataset(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == "GET":
        dataset: Optional[Dataset] = Dataset.objects.filter(pk=pk).first()
        if dataset is None:
            return HttpResponseRedirect(reverse_lazy("dataset_overview"))

        with dataset.path_cleaned as file:
            return get_download_response(file, f"{dataset.display_name}_cleaned.csv")

    return HttpResponseRedirect(reverse_lazy("dataset_overview"))
