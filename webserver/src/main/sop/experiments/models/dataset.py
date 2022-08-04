from __future__ import annotations

import os.path
from enum import Enum, auto

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from experiments.models.managers import DatasetManager, DatasetQuerySet


def get_dataset_upload_path(instance: Dataset, filename: str) -> str:
    user_id = instance.user.id
    return os.path.join("datasets", "user_" + str(user_id), filename)


class CleaningState(Enum):
    RUNNING = auto, False, False
    FINISHED = auto, True, False
    FINISHED_WITH_ERROR = auto, True, True

    def is_cleaned(self) -> bool:
        return self.value[1]

    def has_error(self) -> bool:
        return self.value[2]


class Dataset(models.Model):
    """
    Database Model of a Dataset.
    """

    display_name = models.CharField(max_length=80)
    description = models.TextField(max_length=255, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    datapoints_total = models.IntegerField(null=True)
    dimensions_total = models.IntegerField(null=True)
    path_original = models.FileField(
        upload_to=get_dataset_upload_path,
        validators=(FileExtensionValidator(allowed_extensions=["csv"]),),
    )
    path_cleaned = models.FileField(null=True)
    status = models.CharField(max_length=80)
    has_header = models.BooleanField(default=True)
    objects = DatasetManager.from_queryset(DatasetQuerySet)()  # type: ignore

    @property
    def is_deletable(self) -> bool:
        # Import this here to avoid circular import
        from experiments.models import Experiment

        return not Experiment.objects.get_with_dataset(self).exists()

    @property
    def is_cleaned(self) -> bool:
        status: CleaningState = CleaningState[self.status]
        assert status is not None
        return status.is_cleaned()

    @property
    def has_error(self) -> bool:
        status: CleaningState = CleaningState[self.status]
        assert status is not None
        return status.has_error()

    @property
    def get_error_message(self) -> str:
        assert self.has_error is True
        error_file_path: str = self.path_cleaned.path + ".error"
        with open(error_file_path, "r") as file:
            return file.read()

    def __str__(self) -> str:
        return str(self.display_name) + " | " + str(self.user)



