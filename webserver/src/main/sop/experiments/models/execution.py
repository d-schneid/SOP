import math
import random
from typing import Any

from django.conf import settings
from django.db import models

from backend.task.TaskState import TaskState
from experiments.models.experiment import Experiment
from experiments.models.managers import ExecutionManager, ExecutionQuerySet


def generate_random_seed() -> int:
    bounds = int(math.pow(2, 63))
    return random.randint(0, bounds)


class Execution(models.Model):
    experiment = models.ForeignKey(to=Experiment, on_delete=models.CASCADE)
    status = models.CharField(max_length=80)
    progress = models.FloatField(default=0.0)
    creation_date = models.DateTimeField(auto_now_add=True)
    finished_date = models.DateTimeField(blank=True, null=True)
    subspace_amount = models.IntegerField()
    subspaces_min = models.IntegerField()
    subspaces_max = models.IntegerField()
    subspace_generation_seed = models.BigIntegerField(blank=True)
    algorithm_parameters = models.JSONField()
    result_path = models.FileField()
    objects: ExecutionManager = ExecutionManager.from_queryset(ExecutionQuerySet)()  # type: ignore

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Saves the execution model and generates a random subspace_generation_seed if it has not been set.
        """
        if not self.subspace_generation_seed:
            self.subspace_generation_seed = generate_random_seed()
        super(Execution, self).save(*args, **kwargs)

    @property
    def is_finished(self) -> bool:
        state = TaskState[self.status]
        assert state is not None
        return state.is_finished()

    @property
    def error_occurred(self) -> bool:
        state = TaskState[self.status]
        assert state is not None
        return state.error_occurred()

    @property
    def is_running(self) -> bool:
        state = TaskState[self.status]
        assert state is not None
        return state.is_running()

    @property
    def progress_as_percent(self):
        return self.progress * 100


def get_result_path(execution: Execution) -> str:
    return str(
        settings.MEDIA_ROOT
        / "experiments"
        / ("user_" + str(execution.experiment.user.pk))
        / ("experiment_" + str(execution.experiment.pk))
        / ("execution_" + str(execution.pk))
    )


def get_zip_result_path(execution: Execution) -> str:
    return str(
        settings.MEDIA_ROOT
        / "experiments"
        / ("user_" + str(execution.experiment.user.pk))
        / ("experiment_" + str(execution.experiment.pk))
        / (("execution_" + str(execution.pk)) + ".zip")
    )
