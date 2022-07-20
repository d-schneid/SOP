import uuid

import pandas as pd
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
from experiments.services.dataset import check_if_file_is_csv, save_dataset_finally_uncleaned, path_dataset_finally_cleaned
from experiments.callback import DatasetCallbacks

from backend.task.cleaning import DatasetCleaning


class DatasetUploadView(LoginRequiredMixin, CreateView[Dataset, DatasetUploadForm]):
    model = Dataset
    form_class = DatasetUploadForm
    template_name = "dataset_upload.html"
    success_url = reverse_lazy("dataset_overview")

    def form_valid(self, form):

        temp_file_path: str = self.request.FILES["path_original"].temporary_file_path()

        # check if the file is a csv file
        if not check_if_file_is_csv(temp_file_path):
            form.add_error("path_original", "The given file is not a valid csv.-file.")
            return super(DatasetUploadView, self).form_invalid()

        else:
            # add the model data to the form
            csv_frame: DataFrame = pd.read_csv(temp_file_path)
            form.instance.datapoints_total = csv_frame.shape[0]  # TODO: size vs. shpae[0]
            form.instance.dimensions_total = csv_frame.shape[1]

            form.instance.user = self.request.user
            form.instance.is_cleaned = False
            form.instance.uuid = uuid.uuid1()  # solves the problem that the dataset has (currently) no id
            form.instance.path_original = save_dataset_finally_uncleaned(temp_file_path, str(uuid))
            form.instance.path_cleaned = path_dataset_finally_cleaned(str(uuid))

            # start Dataset Cleaning
            dataset_cleaning: DatasetCleaning = DatasetCleaning(form.instance.user.id,
                                                                form.instance.uuid.int,
                                                                DatasetCallbacks.cleaning_callback,
                                                                form.instance.path_original,
                                                                form.instance.path_cleaned)

            return super(DatasetUploadView, self).form_valid(form)


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

    def form_valid(self, form):
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
