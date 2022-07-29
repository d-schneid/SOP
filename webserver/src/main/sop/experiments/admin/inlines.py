from abc import ABCMeta

from django.contrib import admin
from django.db.models import Model

from experiments.models.experiment import Experiment


class AbstractExperimentInlineMeta(ABCMeta,
                                   type(admin.StackedInline[Model, Experiment])):
    pass


class AbstractExperimentInline(admin.StackedInline[Model, Experiment],
                               metaclass=AbstractExperimentInlineMeta):
    class Meta:
        abstract = True

    def has_add_permission(self, request, obj) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


class ExperimentInlineAlgorithm(AbstractExperimentInline):
    model = Experiment.algorithms.through
    template = "admin/experiment/experiment_inline_algorithm.html"


class ExperimentInlineDataset(AbstractExperimentInline):
    model = Experiment
    template = "admin/experiment/experiment_inline_dataset.html"
    fields = ["display_name"]