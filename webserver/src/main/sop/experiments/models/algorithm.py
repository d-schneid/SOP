from datetime import date

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from experiments.models.managers import AlgorithmManager, AlgorithmQuerySet


def _get_algorithm_upload_path(instance, filename) -> str:
    user_id = instance.user.id if instance.user is not None else 0
    return f"algorithms/user_{user_id}/{filename}"


class Algorithm(models.Model):
    """
    Database model of an algorithm
    """

    class AlgorithmGroup(models.TextChoices):
        PROBABILISTIC = "Probabilistic"
        LINEAR_MODEL = "Linear Model"
        PROXIMITY_BASED = "Proximity-Based"
        OUTLIER_ENSEMBLES = "Outlier Ensembles"
        NEURAL_NETWORKS = "Neural Networks"
        COMBINATION = "Combination"
        OTHER = "Other"

    # TODO: check max_length, blank, and null
    name = models.CharField(max_length=80)
    group = models.CharField(max_length=80, choices=AlgorithmGroup.choices)
    signature = models.CharField(max_length=80)
    path = models.FileField(upload_to=_get_algorithm_upload_path,
                            validators=(FileExtensionValidator(
                                allowed_extensions=["py"]),))
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, blank=True, null=True)

    objects = AlgorithmManager.from_queryset(AlgorithmQuerySet)()

    def __str__(self) -> str:
        return str(self.name)
