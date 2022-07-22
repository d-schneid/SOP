from django.contrib import admin

from experiments.models import Dataset
from experiments.forms.admin.dataset import AdminAddDatasetForm, AdminChangeDatasetForm
from experiments.admin.inlines import ExperimentInlineDataset
from experiments.admin.model import AbstractModelAdmin
<<<<<<< HEAD


@admin.register(Dataset)
class DatasetAdmin(AbstractModelAdmin):
    inlines = [ExperimentInlineDataset]
    list_display = ["display_name", "user", "datapoints_total", "dimensions_total", "upload_date", "is_cleaned"]
    raw_id_fields = ["user"]
    list_filter = ["upload_date", "is_cleaned"]
    search_fields = ["display_name"]
    actions = ["delete_selected"]

    def get_admin_add_form(self):
        return AdminAddDatasetForm

    def get_admin_change_form(self):
        return AdminChangeDatasetForm

    def get_model_name(self):
        return "dataset"



=======


@admin.register(Dataset)
class DatasetAdmin(AbstractModelAdmin):
    inlines = [ExperimentInlineDataset]
    list_display = ["display_name", "user", "datapoints_total", "dimensions_total", "upload_date", "is_cleaned"]
    raw_id_fields = ["user"]
    list_filter = ["upload_date", "is_cleaned"]
    search_fields = ["display_name"]
    actions = ["delete_selected"]

    def get_admin_add_form(self):
        return AdminAddDatasetForm

    def get_admin_change_form(self):
        return AdminChangeDatasetForm

    def get_model_name(self):
        return "dataset"
>>>>>>> 17fdfccdcb15e505bdb720095bd2422279589085
