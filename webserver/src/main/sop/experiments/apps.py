from django.apps import AppConfig
from django.conf import settings

from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler
from backend.task.execution.AlgorithmLoader import AlgorithmLoader


class ExperimentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "experiments"

    def ready(self) -> None:
        from experiments import signals  # noqa
        from experiments.models.managers import ExecutionManager

        AlgorithmLoader.set_algorithm_root_dir(str(settings.ALGORITHM_ROOT_DIR))
        Scheduler.default_scheduler = UserRoundRobinScheduler

        ExecutionManager.mark_running_executions_as_crashed()
