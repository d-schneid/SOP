from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from authentication.models import User

if TYPE_CHECKING:
    from experiments.models import (  # noqa: F401
        Algorithm,
        Dataset,
        Experiment,
        Execution,
    )


class AlgorithmManager(models.Manager["Algorithm"]):
    pass


class AlgorithmQuerySet(models.QuerySet["Algorithm"]):
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


class DatasetManager(models.Manager["Dataset"]):
    pass


class DatasetQuerySet(models.QuerySet["Dataset"]):
    def get_sorted_by_name(self) -> DatasetQuerySet:
        return self.order_by(Lower("display_name"))

    def get_sorted_by_upload_time(self) -> DatasetQuerySet:
        return self.order_by("-upload_date")

    def get_by_user(self, request_user: User) -> DatasetQuerySet:
        return self.filter(user=request_user)


class ExperimentManager(models.Manager["Experiment"]):
    pass


class ExperimentQuerySet(models.QuerySet["Experiment"]):
    def get_sorted_by_name(self) -> ExperimentQuerySet:
        return self.order_by(Lower("display_name"))

    def get_sorted_by_creation_date(self) -> ExperimentQuerySet:
        return self.order_by("-creation_date")

    def get_by_user(self, request_user: User) -> ExperimentQuerySet:
        return self.filter(user=request_user)

    def get_with_dataset(self, request_dataset: Dataset) -> ExperimentQuerySet:
        return self.filter(dataset=request_dataset)


class ExecutionManager(models.Manager["Execution"]):
    pass


class ExecutionQuerySet(models.QuerySet["Execution"]):
    def get_sorted_by_creation_date(self) -> ExecutionQuerySet:
        return self.order_by("-creation_date")

    def get_by_user(self, request_user: User) -> ExecutionQuerySet:
        return self.filter(user=request_user)
