
from abc import ABC, abstractmethod

from collections.abc import Callable

from backend.task.TaskState import TaskState


class Task(ABC):
    """
    An abstract class which sets the structure for all tasks that are computed by the BackendLibrary. \n
    The subclasses are created from outside (e.g. webserver). They also call the schedule() method.
    """

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable[[int, TaskState, float], None]):
        """
        :param user_id: The ID of the user belonging to the task. Has to be at least -1.
        :param task_id: The ID of the task. Has to be at least -1.
        :param task_progress_callback: The task returns its progress with the task_progress_callback.
        """
        assert user_id >= -1
        assert task_id >= -1
        self._user_id: int = user_id
        self._task_id: int = task_id
        self._task_progress_callback: Callable = task_progress_callback

    @abstractmethod
    def schedule(self) -> None:
        """
        Inserts the Task into the Scheduler for processing. \n
        :return: None
        """
        return None
