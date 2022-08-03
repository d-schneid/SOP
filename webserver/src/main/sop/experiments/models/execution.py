import math
import random
from enum import Enum, auto
from typing import Any

from django.conf import settings
from django.db import models

from experiments.models.experiment import Experiment
from experiments.models.managers import ExecutionManager, ExecutionQuerySet


class ExecutionStatus(Enum):
    """
    An Enum that describes the status of an execution. It contains methods for checking
    specific traits of the states, for example if the execution is running or if an
    error occurred.
    """
    RUNNING = auto, False, False, False, True
    RUNNING_WITH_ERROR = auto, False, False, True, True
    FINISHED = auto, False, True, False, False
    FINISHED_WITH_ERROR = auto, False, True, True, False
    CRASHED = auto, True, False, False, False

    def is_crashed(self) -> bool:
        """
        Checks if the execution is crashed.
        @return: True if the execution is crashed, False otherwise.
        """
        return self.value[1]

    def has_result(self) -> bool:
        """
        Checks if the execution has a result.
        @return: True if the execution has a result, False otherwise.
        """
        return self.value[2]

    def error_occurred(self) -> bool:
        """
        Checks if an error occurred in the execution.
        @return: True if an error occurred in the execution, False otherwise.
        """
        return self.value[3]

    def is_running(self) -> bool:
        """
        Checks if the execution is running.
        @return: True, if the execution is running, False otherwise
        """
        return self.value[4]


def generate_random_seed() -> int:
    """
    Generate a random seed in the range [0, 2^63 - 1]
    @return: A randomly generated seed.
    """
    bounds = int(math.pow(2, 63))
    return random.randint(0, bounds)


class Execution(models.Model):
    """
    The database model of an execution
    """
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
        Saves the execution model and generates a random subspace_generation_seed if it
        has not been set.
        @param args:
        @param kwargs:
        @return: None
        """
        if not self.subspace_generation_seed:
            self.subspace_generation_seed = generate_random_seed()
        super(Execution, self).save(*args, **kwargs)

    @property
    def has_result(self) -> bool:
        """
        Checks if the execution has a result.
        @return: True if the execution has a result, False otherwise.
        """
        state = ExecutionStatus[self.status]
        assert state is not None
        return state.has_result()

    @property
    def error_occurred(self) -> bool:
        """
        Checks if an error occurred in the execution.
        @return: True if an error occurred in the execution, False otherwise.
        """
        state = ExecutionStatus[self.status]
        assert state is not None
        return state.error_occurred()

    @property
    def is_running(self) -> bool:
        """
        Checks if the execution is running.
        @return: True, if the execution is running, False otherwise
        """
        state = ExecutionStatus[self.status]
        assert state is not None
        return state.is_running()

    @property
    def is_crashed(self) -> bool:
        """
        Checks if the execution is crashed.
        @return: True if the execution is crashed, False otherwise.
        """
        state = ExecutionStatus[self.status]
        assert state is not None
        return state.is_crashed()

    @property
    def progress_as_percent(self) -> float:
        """
        Gets the progress of the execution in percent.
        @return: The progress of the execution in percent.
        """
        return self.progress * 100


def get_result_path(execution: Execution) -> str:
    """
    Generates a result path for the given execution.
    @param execution: The execution for which results should be stored.
    @return: The path for the results as a string.
    """
    return str(
        settings.MEDIA_ROOT
        / "experiments"
        / ("user_" + str(execution.experiment.user.pk))
        / ("experiment_" + str(execution.experiment.pk))
        / ("execution_" + str(execution.pk))
    )


def get_zip_result_path(execution: Execution) -> str:
    """
    Generates a path where the zipped results should be stored.
    @param execution: The execution for which the zipped results should be stored.
    @return: The path for the zipped resulsts as a string.
    """
    return str(
        settings.MEDIA_ROOT
        / "experiments"
        / ("user_" + str(execution.experiment.user.pk))
        / ("experiment_" + str(execution.experiment.pk))
        / (("execution_" + str(execution.pk)) + ".zip")
    )
