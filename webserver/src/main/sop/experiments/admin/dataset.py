from typing import Type

from django.contrib import admin

from experiments.admin.inlines import ExperimentInlineDataset
from experiments.admin.abstract_model_admin import AbstractModelAdmin
from experiments.forms.admin.dataset import AdminAddDatasetForm, AdminChangeDatasetForm
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

    def get_admin_add_form(self) -> Type[AdminAddDatasetForm]:
        return AdminAddDatasetForm

    def get_admin_change_form(self) -> Type[AdminChangeDatasetForm]:
        return AdminChangeDatasetForm

    def get_model_name(self) -> str:
        return "dataset"
