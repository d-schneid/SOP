import string
from abc import ABC, abstractmethod

from collections.abc import Callable


class Task(ABC):

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable):
        self._user_id: int = user_id
        self._task_id: int = task_id
        self._task_progress_callback: Callable = task_progress_callback

    @abstractmethod
    def schedule(self) -> None:
        return None
