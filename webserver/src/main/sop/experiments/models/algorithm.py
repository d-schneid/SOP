from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.fields.files import FieldFile
from django.urls import reverse

from authentication.models import User
from experiments.models.managers import AlgorithmManager


def _get_algorithm_upload_path(instance, filename) -> str:
    return f"algorithms/user_{instance.user.id}/{filename}"


class Algorithm(models.Model):
    """
    Database model of an algorithm
    """

    # TODO: more groups to be added
    class AlgorithmGroup(models.TextChoices):
        LINEAR_MODEL = "Linear Model"
        PROXIMITY_BASED = "Proximity-based"
        PROBABILISTIC = "Probabilistic"
        OUTLIER_ENSEMBLES = "Outlier Ensembles"
        OTHER = "Other"

    # TODO: check max_length, blank, and null
    _name = models.CharField(max_length=80)
    _group = models.CharField(max_length=80, choices=AlgorithmGroup.choices)
    _signature = models.CharField(max_length=80)
    _path = models.FileField(upload_to=_get_algorithm_upload_path,
                             validators=(FileExtensionValidator(
                                 allowed_extensions=["py"]),))
    _description = models.TextField()
    _user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)

    objects = AlgorithmManager()

    class Meta:
        # TODO: use UniqueConstraint instead
        unique_together = ["_name", "_user"]

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        # TODO: maybe throw exception if value has more than 80 characters?
        self._name = value

    @property
    def group(self) -> str:
        return self._group

    @property
    def signature(self) -> str:
        return self._signature

    @property
    def path(self) -> FieldFile:
        return self._path

    @property
    def description(self) -> str:
        return self._description

    @property
    def user(self) -> User:
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    def __str__(self) -> str:
        return str(self.name) + "|" + str(self.group)
