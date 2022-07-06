from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

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
    name = models.CharField(max_length=80)
    group = models.CharField(max_length=80, choices=AlgorithmGroup.choices)
    signature = models.CharField(max_length=80)
    path = models.FileField(upload_to=_get_algorithm_upload_path,
                            validators=(FileExtensionValidator(
                                allowed_extensions=["py"]),))
    description = models.TextField()
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    objects = AlgorithmManager()

    class Meta:
        # TODO: use UniqueConstraint instead
        unique_together = ["name", "user"]

    def __str__(self) -> str:
        return str(self.name) + " | " + str(self.group)
