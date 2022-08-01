from typing import Type, Optional, Sequence, Any

from django.contrib import admin
from django.http import HttpRequest

from experiments.admin.inlines import ExperimentInlineDataset
from experiments.admin.abstract_model_admin import AbstractModelAdmin
from experiments.forms.admin.dataset import AdminAddDatasetForm
from experiments.models import Dataset
from experiments.services.dataset import schedule_backend


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
            obj.is_cleaned = False
            obj.datapoints_total = None
            obj.dimensions_total = None
            obj.path_cleaned = None

            # save the model, so that the data is also saved
            super().save_model(request, obj, form, change)

            # now, start the cleaning
            schedule_backend(obj)