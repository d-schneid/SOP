from __future__ import annotations

import os.path

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from experiments.models.managers import DatasetManager, DatasetQuerySet


def get_dataset_upload_path(instance: Dataset, filename: str) -> str:
    user_id = instance.user.id
    return os.path.join("datasets", "user_" + str(user_id), filename)


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
    is_cleaned = models.BooleanField(default=False)
    objects = DatasetManager.from_queryset(DatasetQuerySet)()  # type: ignore

    @property
    def is_deletable(self) -> bool:
        # Import this here to avoid circular import
        from experiments.models import Experiment

        return not Experiment.objects.get_with_dataset(self).exists()

    def __str__(self) -> str:
        return str(self.display_name) + " | " + str(self.user)
