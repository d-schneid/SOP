import os
from typing import Callable

from backend.scheduler.Schedulable import Schedulable
from backend.task.TaskState import TaskState
from backend.task.TaskHelper import TaskHelper


class ResultZipper(Schedulable):
    """
    Zips the execution-result after an Execution is complete.
    """
    def __init__(self, user_id: int, task_id: int, error_occurred: bool,
                 task_progress_callback: Callable[[int, TaskState, float], None],
                 path_to_zip: str, zip_running_path: str, final_zip_path: str, is_debug: bool = False):

        """
        :param user_id: The ID of the user belonging to the Execution. Has to be greater than or equal to -1.
        :param task_id: The ID of the task. Has to be greater than or equal to -1.
        :param error_occurred: Did at least one ExecutionElement fail during the Execution
        :param task_progress_callback: The Execution uses this callback to return its progress.
        :param path_to_zip: Absolute path to the directory that should be zipped
        :param zip_running_path: The absolute path to the directory where the result of
        the zipping will be located while the zipping is performed
        :param final_zip_path: The absolute path to the directory where the result of
        the zipping will be located after the zipping is completed
        :param is_debug: If true, the ResultZipper runs in debug mode.
                         In debug mode, e.g. no files are deleted. For specific differences check the relevant
                         method descriptions.
        """

        assert user_id >= -1
        assert task_id >= -1
        assert os.path.isdir(path_to_zip)
        assert not os.path.isfile(zip_running_path)
        assert not os.path.isfile(final_zip_path)

        self._user_id: int = user_id
        self._task_id: int = task_id
        self._error_occurred: bool = error_occurred
        self._task_progress_callback: Callable = task_progress_callback
        self._path_to_zip: str = path_to_zip
        self._zip_running_path: str = zip_running_path
        self._final_zip_path: str = final_zip_path
        self._is_debug = is_debug

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

        If the ResultZipper runs in debug mode, only a directory at the given path will be created.

        :return: None
        """

        # Check for debug mode
        if self._is_debug:
            TaskHelper.create_directory(self._zipped_file_path)
            return

        # Else, proceed with the normal operations

        TaskHelper.zip_dir(zip_path=self._zipped_file_path, dir_path=self._path_to_zip)  # TODO: pfade anschauen
        TaskHelper.del_dir(self._path_to_zip)

        if self._error_occurred:
            self._task_progress_callback(self._task_id, TaskState.FINISHED_WITH_ERROR, 1)
        else:
            self._task_progress_callback(self._task_id, TaskState.FINISHED, 1)



