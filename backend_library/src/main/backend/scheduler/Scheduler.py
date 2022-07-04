from __future__ import annotations

from typing import Callable

from backend_library.src.main.backend.scheduler.Schedulable import Schedulable
from abc import ABC, abstractmethod


class Scheduler(ABC):
    _instance = None

    def __init__(self):
        # This is not thread safe but as you should not try to break that assertion anyway I do not care
        assert Scheduler._instance is None
        Scheduler._instance = self

    @staticmethod
    def get_instance() -> Scheduler:
        return Scheduler._instance

    @abstractmethod
    def schedule(self, to_schedule) -> None:
        pass

    @abstractmethod
    def abort_by_task(self, task_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def abort_by_user(self, user_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def hard_shutdown(self) -> None:
        pass

    @abstractmethod
    def graceful_shutdown(self, on_shutdown_completed: Callable) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_shutting_down(self) -> bool:
        return False
