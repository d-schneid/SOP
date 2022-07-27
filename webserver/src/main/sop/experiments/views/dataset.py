from __future__ import annotations

import os.path
from typing import Optional

from django.db.models.fields.files import FieldFile
from django.http import HttpResponse, HttpRequest
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView

from authentication.mixins import LoginRequiredMixin
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler
from backend.task.cleaning import DatasetCleaning
from experiments.callback import DatasetCallbacks
from experiments.forms.create import DatasetUploadForm
from experiments.forms.edit import DatasetEditForm
from experiments.models import Dataset
from experiments.models.managers import DatasetQuerySet
from experiments.services.dataset import generate_path_dataset_cleaned, save_dataset
from experiments.views.generic import PostOnlyDeleteView


def schedule_backend(dataset: Dataset) -> None:
    # set and save the missing datafield entry for the cleaned csv file
    cleaned_path = generate_path_dataset_cleaned(dataset.path_original.path)

    # create DatasetCleaning object
    dataset_cleaning: DatasetCleaning = DatasetCleaning(
        user_id=dataset.user.pk,
        task_id=dataset.pk,
        task_progress_callback=DatasetCallbacks.cleaning_callback,
        uncleaned_dataset_path=dataset.path_original.path,
        cleaned_dataset_path=cleaned_path,
        cleaning_steps=None,  # can be changed later on
    )

    # TODO: DO NOT do this here. Move it to AppConfig or whatever
    if UserRoundRobinScheduler._instance is None:
        UserRoundRobinScheduler()

    # start the cleaning
    dataset_cleaning.schedule()


class DatasetUploadView(LoginRequiredMixin, CreateView[Dataset, DatasetUploadForm]):
    model = Dataset
    form_class = DatasetUploadForm
    template_name = "dataset_upload.html"
    success_url = reverse_lazy("dataset_overview")

    def form_valid(self, form):
        # save the file temporarily to disk
        temp_file_path: str = save_dataset(
            self.request.FILES["path_original"], self.request.user
        )

        assert os.path.isfile(temp_file_path)

        # check if the file is a csv file

        # TODO: check if correct csv; if no return an error
        #  and delete the file while returning an error
        """
        if not check_if_file_is_csv(temp_file_path):
            form.add_error("path_original", "The given file is not a valid csv.-file.")
            
            os.remove(temp_file_path)
            assert not os.path.isfile(temp_file_path)
            
            return super(DatasetUploadView, self).form_invalid()"""

        # delete temp file
        os.remove(temp_file_path)

        form.instance.user = self.request.user
        form.instance.is_cleaned = False

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
    template_name = "dataset_delete.html"
    success_url = reverse_lazy("dataset_overview")

    def form_valid(self, form) -> None:
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


def get_download_response(file: FieldFile, download_name: str) -> HttpResponse:
    response = HttpResponse(file.read())
    response["Content-Type"] = "text/plain"
    response["Content-Disposition"] = f"attachment; filename={download_name}"
    return response


def download_uncleaned_dataset(
    request: HttpRequest, pk: int
) -> Optional[HttpResponse | HttpResponseRedirect]:
    if request.method == "GET":
        dataset: Optional[Dataset] = Dataset.objects.filter(pk=pk).first()
        if dataset is None:
            return HttpResponseRedirect(reverse_lazy("dataset_overview"))

        with dataset.path_original as file:
            return get_download_response(file, f"{dataset.display_name}.csv")
    return None


def download_cleaned_dataset(
    request: HttpRequest, pk: int
) -> Optional[HttpResponse | HttpResponseRedirect]:
    if request.method == "GET":
        dataset: Optional[Dataset] = Dataset.objects.filter(pk=pk).first()
        if dataset is None or dataset.is_cleaned is False:
            return HttpResponseRedirect(reverse_lazy("dataset_overview"))
        with dataset.path_cleaned as file:
            return get_download_response(file, f"{dataset.display_name}_cleaned.csv")
    return None
