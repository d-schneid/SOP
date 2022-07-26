from typing import Type, Optional, Sequence

from django.contrib import admin
from django.http import HttpRequest

from experiments.admin.inlines import ExperimentInlineDataset
from experiments.admin.abstract_model_admin import AbstractModelAdmin
from experiments.forms.admin.dataset import AdminAddDatasetForm
from experiments.models import Dataset


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

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[Dataset] = None) -> Sequence[str]:
        # for editing an existing experiment
        if not (obj is None):
            readonly_fields = ["dimensions_total",
                               "datapoints_total",
                               "is_cleaned",
                               "user",
                               "upload_date",
                               "path_original",
                               "path_cleaned"]
            if not obj.is_cleaned:
                readonly_fields.remove("path_cleaned")
            return readonly_fields
        # for adding a new experiment
        else:
            return []

    def get_admin_add_form(self) -> Type[AdminAddDatasetForm]:
        return AdminAddDatasetForm

    def get_model_name(self) -> str:
        return "dataset"
