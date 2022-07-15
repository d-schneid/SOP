from typing import Callable

from backend.scheduler.Schedulable import Schedulable
from backend.task.TaskState import TaskState
from backend.task.TaskHelper import TaskHelper


class ResultZipper(Schedulable):
    """ Zips the execution-result after an Execution is complete.
    """
    def __init__(self, user_id: int, task_id: int, error_occurred: bool,
                 task_progress_callback: Callable[[int, TaskState, float], None],
                 path_to_zip: str, zip_running_path: str, final_zip_path: str):
        """
        :param user_id: The ID of the user belonging to the Execution. Has to be at least -1.
        :param task_id: The ID of the task. Has to be at least -1.
        :param error_occurred: Did at least one ExecutionElement fail during the Execution
        :param task_progress_callback: The Execution uses this callback to return its progress.
        :param path_to_zip: Absolute path to the directory that should be zipped
        :param zip_running_path: The absolute path to the directory where the result of
        the zipping will be located while the zipping is performed
        :param final_zip_path: The absolute path to the directory where the result of
        the zipping will be located after the zipping is completed
        """
        assert user_id >= -1
        assert task_id >= -1
        self._user_id: int = user_id
        self._task_id: int = task_id
        self._error_occurred: bool = error_occurred
        self._task_progress_callback: Callable = task_progress_callback
        self._path_to_zip: str = path_to_zip
        self._zip_running_path: str = zip_running_path
        self._final_zip_path: str = final_zip_path

    @property
    def user_id(self) -> int:
        """
        :return: The ID of the user belonging to this ResultZipping (of the Execution).
        """
        return self._user_id

    @property
    def task_id(self) -> int:
        """
        :return: The ID of the task.
        """
        return self._task_id

    @property
    def priority(self) -> int:
        """
        :return: The priority for the Scheduler.
        """
        return 50

    def do_work(self) -> None:
        """
        Zips the given directory and saves the created .zip-file at the given path.
        The given directory is deleted after the zipping took place.
        After the zipping took place, the callback method is used to inform the
        webserver that the execution is finished.
        :return: None
        """
        # TODO: @FINN Mach das bitte neu, sodass die .zip zuerst im zip_running_path erstellt wird und dann zum
        # _final_zip_path verschoben wird
        # Musst du noch gucken, wie du das machst, da die ja auch verschiedene Namen in den Pfaden haben könnten

        TaskHelper.zip_dir(zip_path=self._final_zip_path, dir_path=self._path_to_zip)
        TaskHelper.del_dir(self._path_to_zip)

        self._task_progress_callback(self._task_id, TaskState.FINISHED, 1)  # TODO


