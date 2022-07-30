from typing import Type, Optional, Sequence, List

from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse, re_path
from django.urls.resolvers import URLPattern
from django.utils.html import format_html

from experiments.admin.inlines import ExperimentInlineDataset
from experiments.admin.abstract_model_admin import AbstractModelAdmin
from experiments.forms.admin.dataset import AdminAddDatasetForm
from experiments.models import Dataset
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
        "is_cleaned",
    ]
    raw_id_fields = ["user"]
    list_filter = ["upload_date", "is_cleaned"]
    search_fields = ["display_name"]
    actions = ["delete_selected"]

    def get_admin_add_form(self) -> Type[AdminAddDatasetForm]:
        return AdminAddDatasetForm

    def get_model_name(self) -> str:
        return "dataset"

    def get_readonly_fields(self,
                            request: HttpRequest,
                            obj: Optional[Dataset] = None
    ) -> Sequence[str]:
        # for editing an existing experiment
        if not (obj is None):
            readonly_fields = ["dimensions_total",
                               "datapoints_total",
                               "is_cleaned",
                               "user",
                               "upload_date",
                               "download_uncleaned",
                               "download_cleaned"]
            if not obj.is_cleaned:
                readonly_fields.remove("download_cleaned")
            return readonly_fields
        # for adding a new experiment
        else:
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