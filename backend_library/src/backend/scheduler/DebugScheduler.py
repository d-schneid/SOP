from collections.abc import Callable
from typing import Optional

from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.Scheduler import Scheduler


class DebugScheduler(Scheduler):
    """Simple scheduler for testing, does not do any scheduling or parallelization"""

    def abort_by_task(self, task_id: int) -> None:
        raise NotImplementedError

    def abort_by_user(self, user_id: int) -> None:
        raise NotImplementedError

    def hard_shutdown(self) -> None:
        return None

    def graceful_shutdown(self,
                          on_shutdown_completed: Optional[Callable[[], None]] = None) \
            -> None:
        if on_shutdown_completed is not None:
            on_shutdown_completed()

    def is_shutting_down(self) -> bool:
        return False

    def schedule(self, to_schedule: Schedulable) -> None:
        to_schedule.run_before_on_main()
        r = to_schedule.do_work()
        if r is None:
            r = 0
        to_schedule.run_later_on_main(r)
