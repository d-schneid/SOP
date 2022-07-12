from django.conf import settings
from django.db import models

from experiments.models import Algorithm
from experiments.models import Dataset
from experiments.models.managers import ExperimentManager, ExperimentQuerySet


class Experiment(models.Model):
    """
    Database model of an experiment
    """

    display_name = models.CharField(max_length=80)  # type: ignore
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # type: ignore
    # We do not allow deletion of a dataset if it's used in an experiment
    dataset = models.ForeignKey(to=Dataset, on_delete=models.PROTECT)  # type: ignore
    algorithms = models.ManyToManyField(to=Algorithm)  # type: ignore
    creation_date = models.DateTimeField(auto_now_add=True)  # type: ignore
    objects = ExperimentManager.from_queryset(ExperimentQuerySet)()

    class Meta:
        unique_together = ["display_name", "user"]

    def __str__(self) -> str:
        return str(self.display_name)
