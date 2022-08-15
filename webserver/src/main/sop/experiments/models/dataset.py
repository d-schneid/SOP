from __future__ import annotations

import os.path
from enum import Enum, auto

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from experiments.models.managers import DatasetManager, DatasetQuerySet


def get_dataset_upload_path(instance: Dataset, filename: str) -> str:
    """
    Generates a path to which the uncleaned .csv file of a dataset should be saved to.
    @param instance: The dataset model.
    @param filename: The filename of the .csv file containing the .csv extension.
    @return: The path to which the uncleaned .csv file should be saved to.
    """
    user_id = instance.user.id
    return os.path.join("datasets", "user_" + str(user_id), filename)


class CleaningState(Enum):
    RUNNING = auto, False, False, False
    FINISHED = auto, True, False, True
    FINISHED_WITH_ERROR = auto, True, True, False

    def has_finished(self) -> bool:
        return self.value[1]

    def has_error(self) -> bool:
        return self.value[2]

    def is_cleaned(self) -> bool:
        return self.value[3]


class Dataset(models.Model):
    """
    Database Model of a Dataset.
    """

    display_name = models.CharField(max_length=80)
    description = models.TextField(max_length=255, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    datapoints_total = models.PositiveBigIntegerField(null=True)
    dimensions_total = models.PositiveIntegerField(null=True)
    path_original = models.FileField(
        upload_to=get_dataset_upload_path,
        validators=(FileExtensionValidator(allowed_extensions=["csv"]),),
    )
    path_cleaned = models.FileField(null=True)
    status = models.CharField(max_length=80)
    cleaning_progress = models.FloatField(default=0.0)
    has_header = models.BooleanField(default=True)
    objects = DatasetManager.from_queryset(DatasetQuerySet)()  # type: ignore

    @property
    def is_deletable(self) -> bool:
        """
        Checks if the dataset is deletable. This is not the case if the dataset is used
        in an experiment.
        @return: True, if the dataset is deletable, False otherwise.
        """
        # Import this here to avoid circular import
        from experiments.models import Experiment

        return not Experiment.objects.get_with_dataset(self).exists()

    @property
    def has_finished(self) -> bool:
        status: CleaningState = CleaningState[self.status]
        assert status is not None
        return status.has_finished()

    @property
    def has_error(self) -> bool:
        status: CleaningState = CleaningState[self.status]
        assert status is not None
        return status.has_error()

    @property
    def is_cleaned(self) -> bool:
        status: CleaningState = CleaningState[self.status]
        assert status is not None
        return status.is_cleaned()

    @property
    def get_error_message(self) -> str:
        assert self.has_error is True
        error_file_path: str = self.path_cleaned.path + ".error"
        with open(error_file_path, "r") as file:
            return file.read()

    @property
    def get_representation(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.display_name)
