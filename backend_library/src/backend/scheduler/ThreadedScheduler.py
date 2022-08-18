from collections.abc import Callable
from threading import Thread
from typing import Optional

from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.Scheduler import Scheduler


class ThreadedScheduler(Scheduler):
    """Advanced scheduler for testing; runs all schedulables in new threads"""
    def schedule(self, to_schedule: Schedulable) -> None:
        Thread(target=ThreadedScheduler._run(to_schedule))

    def abort_by_task(self, task_id: int) -> None:
        raise NotImplementedError

    def abort_by_user(self, user_id: int) -> None:
        raise NotImplementedError

    def hard_shutdown(self) -> None:
        pass

    def graceful_shutdown(self,
                          on_shutdown_completed: Optional[Callable[[], None]] = None) \
            -> None:
        raise NotImplementedError

    def is_shutting_down(self) -> bool:
        return False

    @staticmethod
    def _run(to_schedule):
        status = to_schedule.do_work()
        to_schedule.run_later_on_main(0 if status is None else status)
