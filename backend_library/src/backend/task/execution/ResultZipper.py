
from typing import Callable

from backend.scheduler.Schedulable import Schedulable
from backend.task.TaskState import TaskState


class ResultZipper(Schedulable):
    """ Zips the result after an Execution is complete.
    """
    def __init__(self, user_id: int, task_id: int, error_occurred: bool,
                 task_progress_callback: Callable[[int, TaskState, float], None],
                 path_to_zip: str, zipped_file_path: str):
        self._user_id: int = user_id
        self._task_id: int = task_id
        self._error_occurred: bool = error_occurred
        self._task_progress_callback: Callable = task_progress_callback
        self._path_to_zip: str = path_to_zip
        self._zipped_file_path: str = zipped_file_path

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def task_id(self) -> int:
        return self._task_id

    @property
    def priority(self) -> int:
        """
        :return: The priority for the Scheduler.
        """
        return 50

    def do_work(self) -> None:
        return None
