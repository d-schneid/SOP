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
    display_name = models.CharField(max_length=80)  # type: ignore
    group = models.CharField(max_length=80, choices=AlgorithmGroup.choices)  # type: ignore
    signature = models.CharField(max_length=80)  # type: ignore
    path = models.FileField(
        upload_to=_get_algorithm_upload_path,
        validators=(FileExtensionValidator(allowed_extensions=["py"]),),
    )
    description = models.TextField(blank=True)  # type: ignore
    upload_date = models.DateTimeField(auto_now_add=True)  # type: ignore
    user = models.ForeignKey(  # type: ignore
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )

    objects = AlgorithmManager.from_queryset(AlgorithmQuerySet)()

    def __str__(self) -> str:
        return str(self.display_name)
