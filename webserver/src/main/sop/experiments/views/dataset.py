from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from pandas import DataFrame

from authentication.mixins import LoginRequiredMixin
from experiments.forms.create import DatasetUploadForm
from experiments.forms.edit import DatasetEditForm
from experiments.models import Dataset

import pandas as pd


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
        sorted_by_name = Dataset.objects.get_sorted_by_name().filter(user=self.request.user)
        context.update({"models_list": sorted_by_name})
        return context


class DatasetDeleteView(LoginRequiredMixin, DeleteView):
    model = Dataset
    template_name = "experiments/dataset/dataset_delete.html"
    success_url = reverse_lazy("dataset_overview")


class DatasetEditView(LoginRequiredMixin, UpdateView):
    model = Dataset
    form_class = DatasetEditForm
    template_name = "experiments/dataset/dataset_edit.html"
    success_url = reverse_lazy("dataset_overview")
