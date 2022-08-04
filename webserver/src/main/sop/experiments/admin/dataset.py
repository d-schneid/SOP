from typing import Type, Optional, Sequence, List, Any

from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse, re_path
from django.urls.resolvers import URLPattern
from django.utils.html import format_html

from experiments.admin.inlines import ExperimentInlineDataset
from experiments.admin.abstract_model_admin import AbstractModelAdmin
from experiments.forms.admin.dataset import AdminAddDatasetForm, AdminChangeDatasetForm
from experiments.models.dataset import Dataset, CleaningState
from experiments.services.dataset import schedule_backend
from experiments.views.dataset import (
    download_uncleaned_dataset,
    download_cleaned_dataset
)


@admin.register(Dataset)
class DatasetAdmin(AbstractModelAdmin):
    inlines = [ExperimentInlineDataset]
    list_display = [
        "display_name",
        "user",
        "datapoints_total",
        "dimensions_total",
        "upload_date",
        "status",
    ]
    raw_id_fields = ["user"]
    list_filter = ["upload_date", "status"]
    search_fields = ["display_name"]
    actions = ["delete_selected"]

    def get_admin_add_form(self) -> Type[AdminAddDatasetForm]:
        return AdminAddDatasetForm

    def get_admin_change_form(self) -> Type[AdminChangeDatasetForm]:
        return AdminChangeDatasetForm

    def get_model_name(self) -> str:
        return "dataset"

    def get_readonly_fields(self,
                            request: HttpRequest,
                            obj: Optional[Dataset] = None
    ) -> Sequence[str]:
        # for editing an existing experiment
        if not obj is None:
            readonly_fields = ["dimensions_total",
                               "datapoints_total",
                               "status",
                               "user",
                               "upload_date",
                               "download_uncleaned",
                               "download_cleaned"]
            if not obj.is_cleaned:
                readonly_fields.remove("download_cleaned")
            return readonly_fields
        # for adding a new experiment
        return []

    def get_urls(self) -> List[URLPattern]:
        urls = super().get_urls()
        urls += [
            re_path(r'^dataset_download_uncleaned/(?P<pk>\d+)$',
                    download_uncleaned_dataset,
                    name='experiments_dataset_download_uncleaned'),
            re_path(r'^dataset_download_cleaned/(?P<pk>\d+)$',
                    download_cleaned_dataset,
                    name='experiments_dataset_download_cleaned'),
        ]
        return urls

    def save_model(
            self,
            request: Any,
            obj: Dataset,
            form: Any,
            change: Any
    ) -> None:

        # start the dataset cleaning, if it is adding the model (not if it is changing the model)

        if change is not None and change is True:

            # if it is only changing the model, just save it without starting the dataset cleaning
            # (as it is not possible to change the dataset in the admin view)
            super().save_model(request, obj, form, change)

        else:
            # else start the DatasetCleaning and reset possible (wrong) values entered
            obj.status = CleaningState.RUNNING.name
            obj.datapoints_total = None
            obj.dimensions_total = None
            obj.path_cleaned = None

            # save the model, so that the data is also saved
            super().save_model(request, obj, form, change)

            # now, start the cleaning
            schedule_backend(obj)

    def download_uncleaned(self, dataset: Dataset) -> str:
        return format_html(
            '<a href="{}">Download</a>',
            reverse('admin:experiments_dataset_download_uncleaned', args=[dataset.pk])
        )
    download_uncleaned.short_description = "Uncleaned dataset"

    def download_cleaned(self, dataset: Dataset) -> str:
        return format_html(
            '<a href="{}">Download</a>',
            reverse('admin:experiments_dataset_download_cleaned', args=[dataset.pk])
        )
    download_cleaned.short_description = "Cleaned dataset"
