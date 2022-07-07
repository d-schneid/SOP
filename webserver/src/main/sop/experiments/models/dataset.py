from datetime import datetime

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from experiments.models.managers import DatasetManager, DatasetQueryset


def _get_dataset_upload_path(instance, filename) -> str:
    user_id = instance.user.id
    return f"datasets/user{user_id}/{filename}"


class Dataset(models.Model):
    """
    Database Model of a Dataset.
    """

    name = models.CharField(max_length=80)
    description = models.TextField(max_length=255, blank=True)
    upload_date = models.DateTimeField(default=datetime.now())
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    datapoints_total = models.IntegerField()
    dimensions_total = models.IntegerField()
    path_original = models.FileField(upload_to=_get_dataset_upload_path,
                                     validators=(FileExtensionValidator(allowed_extensions=["csv"]),))
    path_cleaned = models.FileField(null=True)
    is_cleaned = models.BooleanField(default=False)
    objects = DatasetManager.from_queryset(DatasetQueryset)()

    class Meta:
        """
        Contains meta-information about Dataset Model
        """

    def __str__(self) -> str:
        return str(self.name) + " | " + str(self.user)


def get_dataset_path(instance: Dataset, filename: str) -> str:
    return f"datasets/user_{instance.user.pk}/{filename}"
