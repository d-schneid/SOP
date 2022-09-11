import logging
import os
import signal
import sys
import types

from django.apps import AppConfig
from django.conf import settings

from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler
from backend.task.execution.AlgorithmLoader import AlgorithmLoader


def hard_shutdown(signum: int, frame: types.FrameType):
    Scheduler.get_instance().hard_shutdown()


class ExperimentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "experiments"

    def ready(self) -> None:
        from experiments import signals  # noqa

        # logging
        loglevel = logging.getLevelName(os.environ.get("SOP_LOG_LEVEL", "INFO"))
        logging.basicConfig(stream=sys.stdout, level=loglevel)

        # backend initializations
        AlgorithmLoader.set_algorithm_root_dir(str(settings.ALGORITHM_ROOT_DIR))
        Scheduler.default_scheduler = UserRoundRobinScheduler

        # signal handler or shutting down the scheduler and all running processes
        signal.signal(signal.SIGTERM, hard_shutdown)
