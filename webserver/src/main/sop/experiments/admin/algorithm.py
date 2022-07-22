from __future__ import annotations

from django.contrib import admin

from experiments.forms.admin.algorithm import AdminAddAlgorithmForm, AdminChangeAlgorithmForm
from experiments.models.algorithm import Algorithm
from experiments.admin.inlines import ExperimentInlineAlgorithm
from experiments.admin.model import AbstractModelAdmin


@admin.register(Algorithm)
class AlgorithmAdmin(AbstractModelAdmin):
    inlines = [ExperimentInlineAlgorithm]
    list_display = ["display_name", "group", "user", "upload_date"]
    raw_id_fields = ["user"]
    list_filter = ["upload_date", "group"]
    search_fields = ["display_name"]
    actions = ["delete_selected"]

    def get_admin_add_form(self):
        return AdminAddAlgorithmForm

    def get_admin_change_form(self):
        return AdminChangeAlgorithmForm

    def get_model_name(self):
        return "algorithm"