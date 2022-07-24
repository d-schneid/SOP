from django.db import models

from backend.task.TaskState import TaskState
from experiments.models.experiment import Experiment
from experiments.models.managers import ExecutionManager, ExecutionQuerySet


class Execution(models.Model):
    experiment = models.ForeignKey(to=Experiment, on_delete=models.CASCADE)
    status = models.CharField(max_length=80, default="created")
    progress = models.FloatField(default=0.0)
    creation_date = models.DateTimeField(auto_now_add=True)
    finished_date = models.DateTimeField(blank=True, null=True)
    subspace_amount = models.IntegerField()
    subspaces_min = models.IntegerField()
    subspaces_max = models.IntegerField()
    subspace_generation_seed = models.BigIntegerField(blank=True)
    algorithm_parameters = models.JSONField()
    result_path = models.FileField()
    objects: ExecutionManager = ExecutionManager.from_queryset(ExecutionQuerySet)()

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
