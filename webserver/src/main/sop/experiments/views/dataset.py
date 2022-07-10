from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from pandas import DataFrame

from authentication.mixins import LoginRequiredMixin
from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler
from experiments.forms.create import DatasetUploadForm
from experiments.forms.edit import DatasetEditForm
from experiments.models.dataset import Dataset, get_dataset_path
from django.core.files.uploadhandler import TemporaryUploadedFile

import pandas as pd

from experiments.models.managers import DatasetQueryset
from backend.task.cleaning import DatasetCleaning
from django.conf import settings


def stub_callback(*args, **kwargs):
    print("CALLBACK:")
    for arg in args:
        print(arg)
    print()


def begin_dataset_cleaning(dataset: Dataset):
    cleaning = DatasetCleaning(
        uncleaned_dataset_path=str(settings.MEDIA_ROOT / str(dataset.path_original)),
        cleaned_dataset_path=str(settings.MEDIA_ROOT / str(dataset.path_cleaned)),
        cleaning_steps=None,
        task_id=dataset.pk,
        user_id=dataset.user.pk,
        task_progress_callback=stub_callback,
    )
    print(dataset.path_cleaned)
    print(dataset.path_original)
    if Scheduler._instance is None:
        DebugScheduler()
    cleaning.schedule()


class DatasetUploadView(LoginRequiredMixin, CreateView):
    model = Dataset
    form_class = DatasetUploadForm
    template_name = "dataset_upload.html"
    success_url = reverse_lazy("dataset_overview")

    def form_valid(self, form):
        form.instance.user = self.request.user
        file: TemporaryUploadedFile = self.request.FILES["path_original"]

        csv_frame: DataFrame = pd.read_csv(
            file.temporary_file_path()
        )
        form.instance.datapoints_total = csv_frame.size
        form.instance.dimensions_total = csv_frame.shape[1]

        form.instance.is_cleaned = False

        # create dataset so we can extract attributes of dataset later
        response = super().form_valid(form)
        form.instance.path_cleaned = str(form.instance.path_original).split(".")[0] + "_cleaned.csv"
        begin_dataset_cleaning(form.instance)
        return response


class DatasetOverview(LoginRequiredMixin, ListView):
    model = Dataset
    template_name = "dataset_overview.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        datasets: DatasetQueryset = Dataset.objects.get_by_user(self.request.user)

        # Sorting
        sort_by: str = self.kwargs["sort"]
        if sort_by == "upload_date":
            datasets = datasets.get_sorted_by_upload_time()
        else:
            datasets = datasets.get_sorted_by_name()

        context.update({"models_list": datasets})
        return context


class DatasetDeleteView(LoginRequiredMixin, DeleteView):
    model = Dataset
    template_name = "dataset_delete.html"
    success_url = reverse_lazy("dataset_overview")

    def form_valid(self, form):
        # processing before object is deleted
        # access object and its fields
        dataset: Dataset = self.get_object()

        # find experiment via related name in models of experiment
        if not dataset.is_deletable:
            # return reverse_lazy("dataset_overview")
            return HttpResponseRedirect(reverse_lazy("dataset_overview"))
        return super().form_valid(form)


class DatasetEditView(LoginRequiredMixin, UpdateView):
    model = Dataset
    form_class = DatasetEditForm
    template_name = "dataset_edit.html"
    success_url = reverse_lazy("dataset_overview")
