from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional

from backend.scheduler.Schedulable import Schedulable


class Scheduler(ABC):
    """Abstract class for implementing schedulers"""
    _instance: Optional[Scheduler] = None
    default_scheduler: Callable[[], Scheduler] = None
    """Defines a standard Scheduler to be created if get_instance is called and none exists"""

    def __init__(self):
        """Ensures that there is only one Scheduler at any point in time"""
        # This is not thread safe
        # but as you should not try to break that assertion anyway I do not care
        assert Scheduler._instance is None, "A scheduler has already been created"
        Scheduler._instance = self

    @staticmethod
    def get_instance() -> Scheduler:
        """Gets the current scheduler, default_scheduler is created when none exists
        :raises AssertionError when default_scheduler and _instance is None"""
        if Scheduler._instance is None:
            assert Scheduler.default_scheduler is not None, \
                "A scheduler is yet to be created"
            return Scheduler.default_scheduler()
        return Scheduler._instance

    @abstractmethod
    def schedule(self, to_schedule: Schedulable) -> None:  # pragma: no cover
        """schedules a given Schedulable for processing"""
        pass

    @abstractmethod
    def abort_by_task(self, task_id: int) -> None:  # pragma: no cover
        """Aborts all Tasks matching a Task id.
        Aborts do not happen whilst running run_before_on_main or run_later_on_main.
        :raises NotImplementedError if not supported
        :raises Value error optionally if -1 is provided as task_id"""
        pass

    @abstractmethod
    def abort_by_user(self, user_id: int) -> None:  # pragma: no cover
        """Aborts all Tasks matching a User id
         :raises NotImplementedError if not supported
         :raises Value error optionally if -1 is provided as user_id"""
        pass

    @abstractmethod
    def hard_shutdown(self) -> None:  # pragma: no cover
        """Terminates all work now, scheduler might not be usable after calling this"""
        pass

    @abstractmethod
    def graceful_shutdown(self, on_shutdown_completed: Callable) -> None:  # pragma: no cover
        """Waits for active Tasks to finish, no new ones are started after this.
        If called after a tasks run_before_on_main started but before do_work started,
        the task may or may not be aborted.
        :raises NotImplementedError if not supported"""
        pass

    @abstractmethod
    def is_shutting_down(self) -> bool:  # pragma: no cover
        """Returns whether a graceful shutdown is ongoing,
        false if that feature is not supported """
        pass
