from typing import Callable, Type

from backend_library.src.main.backend.scheduler.Schedulable import Schedulable
from backend_library.src.main.backend.scheduler.Scheduler import Scheduler


class DebugScheduler(Scheduler):
    def abort_by_task(self, task_id: int) -> None:
        raise NotImplementedError

    def abort_by_user(self, user_id: int) -> None:
        raise NotImplementedError

    def hard_shutdown(self) -> None:
        return None

    def graceful_shutdown(self, on_shutdown_completed: Callable) -> None:
        raise NotImplementedError

    def is_shutting_down(self) -> bool:
        return False

    def schedule(self, to_schedule: Schedulable) -> None:
        to_schedule.do_work()
