from django.db import models

from backend.task.TaskState import TaskState
from experiments.models.experiment import Experiment
from experiments.models.managers import ExecutionManager, ExecutionQuerySet


class Execution(models.Model):
    experiment = models.ForeignKey(to=Experiment, on_delete=models.CASCADE)  # type: ignore
    status = models.CharField(max_length=80, default="created")  # type: ignore
    progress = models.FloatField(default=0.0)  # type: ignore
    creation_date = models.DateTimeField(auto_now_add=True)  # type: ignore
    finished_date = models.DateTimeField(blank=True, null=True)  # type: ignore
    subspace_amount = models.IntegerField()  # type: ignore
    subspaces_min = models.IntegerField()  # type: ignore
    subspaces_max = models.IntegerField()  # type: ignore
    subspace_generation_seed = models.BigIntegerField(blank=True)  # type: ignore
    algorithm_parameters = models.JSONField()
    result_path = models.FileField()
    objects = ExecutionManager.from_queryset(ExecutionQuerySet)()

    @property
    def is_finished(self):
        state = TaskState[self.status]
        assert state is not None
        return state.is_finished()

    @property
    def error_occurred(self):
        state = TaskState[self.status]
        assert state is not None
        return state.error_occurred()

    @property
    def is_running(self):
        state = TaskState[self.status]
        assert state is not None
        return state.is_running()
