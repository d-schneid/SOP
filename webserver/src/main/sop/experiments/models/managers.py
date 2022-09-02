from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from authentication.models import User

if TYPE_CHECKING:
    # must be done this way to avoid circular import issues
    from experiments.models import (  # noqa: F401
        Algorithm,
        Dataset,
        Experiment,
        Execution,
    )


class AlgorithmManager(models.Manager["Algorithm"]):
    pass


class AlgorithmQuerySet(models.QuerySet["Algorithm"]):
    """
    A QuerySet that has extra sort and filter functionality specific to algorithm
    models.
    """

    def get_sorted_by_group_and_name(self) -> AlgorithmQuerySet:
        return self.order_by("group", Lower("display_name"))

    def get_sorted_by_name(self) -> AlgorithmQuerySet:
        return self.order_by(Lower("display_name"))

    def get_sorted_by_upload_date(self) -> AlgorithmQuerySet:
        # latest uploaded algorithms first
        return self.order_by("-upload_date")

    def get_with_group(self, group: Algorithm.AlgorithmGroup) -> AlgorithmQuerySet:
        return self.filter(group=group)

    def get_by_user_and_public(self, user: User) -> AlgorithmQuerySet:
        return self.filter(Q(user_id__exact=user.id) | Q(user_id__exact=None))

    def get_by_user(self, user: User) -> AlgorithmQuerySet:
        return self.filter(user__id__exact=user.id)

    def get_public(self) -> AlgorithmQuerySet:
        return self.filter(user=None)

    def get_pyod(self) -> AlgorithmQuerySet:
        return self.filter(user=None)


class DatasetManager(models.Manager["Dataset"]):
    pass


class DatasetQuerySet(models.QuerySet["Dataset"]):
    """
    A QuerySet that has extra sort and filter functionality specific to dataset models.
    """

    def get_sorted_by_name(self) -> DatasetQuerySet:
        return self.order_by(Lower("display_name"))

    def get_sorted_by_upload_time(self) -> DatasetQuerySet:
        return self.order_by("-upload_date")

    def get_by_user(self, request_user: User) -> DatasetQuerySet:
        return self.filter(user=request_user)


class ExperimentManager(models.Manager["Experiment"]):
    pass


class ExperimentQuerySet(models.QuerySet["Experiment"]):
    """
    A QuerySet that has extra sort and filter functionality for experiment models.
    """

    def get_sorted_by_name(self) -> ExperimentQuerySet:
        return self.order_by(Lower("display_name"))

    def get_sorted_by_creation_date(self) -> ExperimentQuerySet:
        return self.order_by("-creation_date")

    def get_by_user(self, request_user: User) -> ExperimentQuerySet:
        return self.filter(user=request_user)

    def get_with_dataset(self, request_dataset: Dataset) -> ExperimentQuerySet:
        return self.filter(dataset=request_dataset)


class ExecutionManager(models.Manager["Execution"]):
    """
    A model manager containing methods that operate on execution models.
    """

    @staticmethod
    def mark_running_executions_as_crashed():
        # must be done this way to avoid circular import issues
        from experiments.models.execution import Execution, ExecutionStatus  # noqa F811

        for execution in Execution.objects.all():
            if execution.is_running:
                execution.status = ExecutionStatus.CRASHED.name
                execution.save()


class ExecutionQuerySet(models.QuerySet["Execution"]):
    """
    A QuerySet that has extra sort and filter functionality specific to execution
    models.
    """

    def get_sorted_by_creation_date(self) -> ExecutionQuerySet:
        return self.order_by("creation_date")

    def get_by_user(self, request_user: User) -> ExecutionQuerySet:
        return self.filter(experiment__user=request_user)
