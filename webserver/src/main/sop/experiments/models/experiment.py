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
    _display_name = models.CharField(max_length=80)
    _user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    # We do not allow deletion of a dataset if it's used in an experiment
    _dataset = models.ForeignKey(to=Dataset, on_delete=models.PROTECT,
                                 related_name="experiment")
    _algorithms = models.ManyToManyField(to=Algorithm)
    _creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["_display_name", "_user"]

    @property
    def display_name(self) -> str:
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        # TODO: maybe throw exception if value has more than 80 characters?
        self._display_name = value

    @property
    def user(self) -> User:
        return self._user

    @property
    def dataset(self) -> Dataset:
        return self._dataset

    @property
    def algorithms(self) -> Manager:
        return self._algorithms

    @property
    def creation_date(self) -> datetime:
        return self._creation_date

    def __str__(self) -> str:
        return str(self.display_name)
