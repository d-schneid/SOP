from __future__ import annotations

from typing import Union, Optional, Any

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from experiments.models.managers import AlgorithmManager, AlgorithmQuerySet

HyperparameterTypes = Optional[Union[str, int, float, list[Any], dict[Any, Any]]]


def get_algorithm_upload_path(instance: Algorithm, filename: str) -> str:
    """
    Generates a path relative to MEDIA_ROOT to which the .py file of the algorithm
    should be saved. It will NOT save the algorithm.
    @param instance: The algorithm model of which the .py file should be saved.
    @param filename: The name of the .py file with extension (i.e. 'algorithm.py')
    @return: The path to which the algorithm should be saved to as a string.
    """
    user_id = instance.user.pk if instance.user is not None else 0
    return f"algorithms/user_{user_id}/{filename}"


class Algorithm(models.Model):
    """
    Database model of an algorithm
    """

    class AlgorithmGroup(models.TextChoices):
        """
        An Enum that describes the way an algorithm does its calculations.
        """

        COMBINATION = "Combination"
        GRAPH_BASED = "Graph-Based"
        LINEAR_MODEL = "Linear Model"
        NEURAL_NETWORKS = "Neural Networks"
        OUTLIER_ENSEMBLES = "Outlier Ensembles"
        PROBABILISTIC = "Probabilistic"
        PROXIMITY_BASED = "Proximity-Based"
        OTHER = "Other"

    # TODO: check max_length, blank, and null
    display_name = models.CharField(max_length=80)
    group = models.CharField(max_length=80, choices=AlgorithmGroup.choices)
    signature = models.JSONField()
    path = models.FileField(
        upload_to=get_algorithm_upload_path,
        validators=(FileExtensionValidator(allowed_extensions=["py"]),),
        max_length=255,
    )
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )

    objects = AlgorithmManager.from_queryset(AlgorithmQuerySet)()  # type: ignore

    def get_signature_as_dict(self) -> dict[str, HyperparameterTypes]:
        """
        Gets the signature of the algorithm. This is a dictionary that maps parameter
        name to parameter default value.
        @return: signature dictionary.
        """
        assert isinstance(self.signature, dict)
        return self.signature

    def __str__(self) -> str:
        return str(self.display_name)
