from django.conf import settings
from django.db import models

from authentication.models import User
from experiments.models.managers import DatasetManager


class Dataset(models.Model):
    """
    Database Model of a Dataset.
    """
    _name = models.CharField(max_length=80)
    _description = models.TextField(max_length=255)
    _user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    _datapoints_total = models.IntegerField()
    _dimensions_total = models.IntegerField()
    _path_original = models.FileField()
    _path_cleaned = models.FilePathField()
    _is_cleaned = models.BooleanField()
    objects = DatasetManager()

    class Meta:
        """
        Contains meta-information about Dataset Model
        """
        unique_together = ["_name", "_user"]

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def user(self) -> User:
        return self._user

    @property
    def datapoints_total(self) -> int:
        return self._datapoints_total

    @property
    def dimensions_total(self) -> int:
        return self._dimensions_total

    @property
    def path_original(self) -> str:
        return self._path_original.path

    @property
    def path_cleaned(self) -> str:
        return self._path_cleaned

    @property
    def is_cleaned(self) -> bool:
        return self._is_cleaned

    def __str__(self) -> str:
        return str(self._name) + "|" + str(self._user)


def get_dataset_path(instance: Dataset, filename: str) -> str:
    return f"datasets/user_{instance.user.pk}/{filename}"
