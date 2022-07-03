import string
from abc import ABC, abstractmethod

from collections.abc import Callable

import TaskState


class Task(ABC):
    """
    An abstract class which sets the structure for all tasks that are computed by the BackendLibrary.
    The subclasses are created from outside (e.g. webserver). They also call the schedule() method.
    """

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable[[int, TaskState, float], None]):
        """
        :param user_id: The ID of the user belonging to the task.
        :param task_id: The ID of the task.
        :param task_progress_callback: The task returns its progress with the task_progress_callback.
        """
        self._user_id: int = user_id
        self._task_id: int = task_id
        self._task_progress_callback: Callable = task_progress_callback

    @abstractmethod
    def schedule(self) -> None:
        """
        Inserts the Task into the Scheduler for processing.
        :return: None
        """
        return None
