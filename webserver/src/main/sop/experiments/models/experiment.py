from django.conf import settings
from django.db import models

from experiments.models import Algorithm
from experiments.models import Dataset
from experiments.models.managers import ExperimentManager, ExperimentQuerySet


class Experiment(models.Model):
    """
    Database model of an experiment
    """

    # TODO: Wtf happened here, why verbose name "Experiment" for the display_name?
    display_name = models.CharField(max_length=80, verbose_name="Experiment")
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # We do not allow deletion of a dataset if it's used in an experiment
    dataset = models.ForeignKey(to=Dataset, on_delete=models.PROTECT)
    algorithms = models.ManyToManyField(to=Algorithm)
    creation_date = models.DateTimeField(auto_now_add=True)
    objects = ExperimentManager.from_queryset(ExperimentQuerySet)()  # type: ignore

    def __str__(self) -> str:
        return str(self.display_name)
