from abc import ABCMeta

from django.contrib import admin
from django.db.models import Model

from experiments.models.experiment import Experiment


class AbstractExperimentInlineMeta(ABCMeta,
                                   type(admin.StackedInline[Model, Experiment])):
    pass


class AbstractExperimentInline(admin.StackedInline[Model, Experiment],
                               metaclass=AbstractExperimentInlineMeta):
    """
    An abstract class that manages permissions for inlines of the Experiment model in
    the admin interface.
    """
    class Meta:
        abstract = True

    def has_add_permission(self, request, obj) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


class ExperimentInlineAlgorithm(AbstractExperimentInline):
    """
    The inlines of the Experiment model for the Algorithm model in the admin interface.
    Is used in the admin interface to display all Experiment model instances that use
    the respective Algorithm model instance.
    """
    model = Experiment.algorithms.through
    template = "admin/experiment/experiment_inline_algorithm.html"


class ExperimentInlineDataset(AbstractExperimentInline):
    """
    The inlines of the Experiment model for the Dataset model in the admin interface.
    Is used in the admin interface to display all Experiment model instances that use
    the respective Dataset model instance.
    """
    model = Experiment
    template = "admin/experiment/experiment_inline_dataset.html"
    fields = ["display_name"]
