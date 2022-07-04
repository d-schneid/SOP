from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

from .validators import validate_file_extension
from .managers import AlgorithmManager


class DatasetModel(models.Model):
    pass

def _get_algorithm_upload_path(instance, filename) -> str:
    return f"algorithms/user_{instance.user.id}/{filename}"

class AlgorithmModel(models.Model):
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
                             validators=(validate_file_extension,
                                         FileExtensionValidator(allowed_extensions=[".py"]),))
    _description = models.TextField()
    _user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    objects = AlgorithmManager()

    class Meta:
        # TODO: use UniqueConstraint instead
        unique_together =["_name", "_user"]

    @property
    def name(self) -> models.CharField:
        return self._name

    @name.setter
    def name(self, value):
        # TODO: maybe throw exception if value has more than 80 characters?
        self._name = value

    @property
    def group(self) -> models.CharField:
        return self._group

    @property
    def signature(self) -> models.CharField:
        return self._signature

    @property
    def path(self) -> models.FileField:
        return self._path

    @property
    def description(self) -> models.TextField:
        return self._description

    @property
    def user(self) -> models.ForeignKey:
        return self._user

    def __str__(self) -> str:
        return str(self.name) + "|" + str(self.group)


class ExperimentModel(models.Model):
    """
    Database model of an experiment
    """
    _display_name = models.CharField(max_length=80)
    _user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    # We do not allow deletion of a dataset if it's used in an experiment
    _dataset = models.ForeignKey(to=DatasetModel, on_delete=models.PROTECT,
                                 related_name="experiment")
    _algorithms = models.ManyToManyField(to=AlgorithmModel)
    _creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["_display_name", "_user"]

    @property
    def display_name(self) -> models.CharField:
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        # TODO: maybe throw exception if value has more than 80 characters?
        self._display_name = value

    @property
    def user(self) -> models.ForeignKey:
        return self._user

    @property
    def dataset(self) -> models.ForeignKey:
        return self._dataset

    @property
    def algorithms(self) -> models.ManyToManyField:
        return self._algorithms

    @property
    def creation_date(self) -> models.DateTimeField:
        return self._creation_date

    def __str__(self) -> str:
        return str(self.display_name)


class ExecutionModel(models.Model):
    pass
