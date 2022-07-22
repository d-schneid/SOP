from django.contrib import admin
from django.db.models import Model

from experiments.models.experiment import Experiment


class ExperimentInline(admin.StackedInline[Model, Experiment]):
    model = Experiment.algorithms.through
    verbose_name = "Experiment"
    template = "experiment_inline.html"

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class ExperimentInlineAlgorithm(ExperimentInline):
    model = Experiment.algorithms.through

class ExperimentInlineDataset(ExperimentInline):
    model = Experiment
    fields = ["display_name", "link_to_B"]