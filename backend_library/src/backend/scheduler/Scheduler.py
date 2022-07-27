from __future__ import annotations

from multiprocessing import Manager
from typing import Callable, Optional

from backend.scheduler.Schedulable import Schedulable
from abc import ABC, abstractmethod


class Scheduler(ABC):
    """Abstract class for implementing scheduling"""
    _instance: Optional[Scheduler] = None
    _manager: Manager = Manager()

    @staticmethod
    def get_manager() -> Manager:
        """Retrieves the cached Manager"""
        return Scheduler._manager

    def __init__(self):
        """Ensures that there is only one Scheduler at any point in time"""
        # This is not thread safe
        # but as you should not try to break that assertion anyway I do not care
        assert Scheduler._instance is None, "A scheduler has already been created"
        Scheduler._instance = self

    @staticmethod
    def get_instance() -> Scheduler:
        """Gets the current scheduler
        :raises AssertionError when none exists"""
        assert Scheduler._instance is not None, "A scheduler is yet to be created"
        return Scheduler._instance

    @abstractmethod
    def schedule(self, to_schedule: Schedulable) -> None:
        """schedules a given Schedulable for processing"""
        pass

    @abstractmethod
    def abort_by_task(self, task_id: int) -> None:
        """Aborts all Tasks matching a Task id
         :raises NotImplementedError if not supported"""
        pass

    @abstractmethod
    def abort_by_user(self, user_id: int) -> None:
        """Aborts all Tasks matching a User id
         :raises NotImplementedError if not supported"""
        pass

    @abstractmethod
    def hard_shutdown(self) -> None:
        """Terminates all work now, scheduler might not be usable after calling this"""
        pass

    @abstractmethod
    def graceful_shutdown(self, on_shutdown_completed: Callable) -> None:
        """Waits for active Tasks to finish, no new ones are started after this
         :raises NotImplementedError if not supported"""
        pass

    @abstractmethod
    def is_shutting_down(self) -> bool:
        """Returns whether a graceful shutdown is ongoing,
        false if that feature is not supported """
        pass
