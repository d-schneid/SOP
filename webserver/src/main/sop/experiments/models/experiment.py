from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import Manager

from experiments.models import Algorithm
from experiments.models import Dataset
from authentication.models import User


class Experiment(models.Model):
    """
    Database model of an experiment
    """

    display_name = models.CharField(max_length=80)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # We do not allow deletion of a dataset if it's used in an experiment
    dataset = models.ForeignKey(
        to=Dataset, on_delete=models.PROTECT, related_name="experiment"
    )
    algorithms = models.ManyToManyField(to=Algorithm)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["display_name", "user"]

    def __str__(self) -> str:
        return str(self.display_name)
