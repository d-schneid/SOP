from collections.abc import Callable
from typing import Optional

from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.Scheduler import Scheduler


class DebugScheduler2(Scheduler):
    """
    Placeholder for a Scheduler that doesn't even start the Schedulables when calling schedule()
    """

    def __init__(self):
        Scheduler.__init__(self)
        self._called_scheduler_amount = 0

    def abort_by_task(self, task_id: int) -> None:
        raise NotImplementedError

    def abort_by_user(self, user_id: int) -> None:
        raise NotImplementedError

    def hard_shutdown(self) -> None:
        return None

    def graceful_shutdown(self,
                          on_shutdown_completed: Optional[Callable[[], None]] = None) \
            -> None:
        raise NotImplementedError

    def is_shutting_down(self) -> bool:
        return False

    def schedule(self, to_schedule: Schedulable) -> None:
        self._called_scheduler_amount += 1
        # Don't schedule anything!

    @property
    def called_scheduler_amount(self) -> int:
        return self._called_scheduler_amount
