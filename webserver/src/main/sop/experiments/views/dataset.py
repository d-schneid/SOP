from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from pandas import DataFrame

from authentication.mixins import LoginRequiredMixin
from experiments.forms.create import DatasetUploadForm
from experiments.forms.edit import DatasetEditForm
from experiments.models import Dataset, Experiment

import pandas as pd

from experiments.models.managers import DatasetQueryset, ExperimentQueryset


class DatasetUploadView(LoginRequiredMixin, CreateView):
    model = Dataset
    form_class = DatasetUploadForm
    template_name = "experiments/dataset/dataset_upload.html"
    success_url = reverse_lazy("dataset_overview")

    def form_valid(self, form):
        form.instance.user = self.request.user

        csv_frame: DataFrame = pd.read_csv(self.request.FILES["path_original"].temporary_file_path())
        form.instance.datapoints_total = csv_frame.size
        form.instance.dimensions_total = csv_frame.shape[1]

        form.instance.is_cleaned = False
        # TODO: Start Dataset Cleaning

        return super().form_valid(form)


class DatasetOverview(LoginRequiredMixin, ListView):
    model = Dataset
    template_name = "experiments/dataset/dataset_overview.html"

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
    template_name = "experiments/dataset/dataset_delete.html"
    success_url = reverse_lazy("dataset_overview")

    def form_valid(self, form):
        # processing before object is deleted
        # access object and its fields
        dataset: Dataset = self.get_object()

        # find experiment via related name in models of experiment
        if not dataset.is_deletable:
            # return reverse_lazy("dataset_overview")
            return HttpResponseRedirect(reverse_lazy('dataset_overview'))
        return super().form_valid(form)


class DatasetEditView(LoginRequiredMixin, UpdateView):
    model = Dataset
    form_class = DatasetEditForm
    template_name = "experiments/dataset/dataset_edit.html"
    success_url = reverse_lazy("dataset_overview")
