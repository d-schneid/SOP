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
                 dir_path: str, zip_path_running: str, zip_path_final: str, is_debug: bool = False):

        """
        :param user_id: The ID of the user belonging to the Execution. Has to be greater than or equal to -1.
        :param task_id: The ID of the task. Has to be greater than or equal to -1.
        :param error_occurred: Did at least one ExecutionElement fail during the Execution?
        :param task_progress_callback: The Execution calls this callback to return its progress.
        :param dir_path: Absolute path to the directory that should be zipped.
        :param zip_path_running: The absolute path to the directory where the result of
        the zipping will be located while the zipping is performed.
        Any existing file will be deleted and overwritten.
        :param zip_path_final: The absolute path to the directory where the result of
        the zipping will be located after the zipping is completed.
        Any existing file will be deleted and overwritten.
        :param is_debug: If true, the ResultZipper runs in debug mode.
                         In debug mode, e.g. no files are deleted. For specific differences check the relevant
                         method descriptions.
        """

        assert user_id >= -1
        assert task_id >= -1
        assert os.path.isdir(dir_path)

        self._user_id: int = user_id
        self._task_id: int = task_id
        self._error_occurred: bool = error_occurred
        self._task_progress_callback: Callable = task_progress_callback
        self._dir_path: str = dir_path
        self._zip_path_running: str = zip_path_running
        self._zip_path_final: str = zip_path_final
        self._is_debug = is_debug

        # if there are files existing at the paths zip_path_running and zip_path_final, delete them
        #  to ensure the correct operation of the following modules
        for file in [self._zip_path_running, self._zip_path_final]:
            if os.path.isfile(file):
                os.remove(file)

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
        Zips the given directory and saves the created .zip-file at the given final path.

        The given directory is deleted after the zipping took place.
        After the zipping took place, the callback method is used to inform the
        webserver that the execution is finished.

        During creation-time, the zip-file will be stored at the path zip_path_running,
        and moved to the path zip_path_final after the creation has finished. This is to ensure that a corrupted
        file can be spotted, e.g. after a server crash. For this to work, both paths have to be located
        in the same file system.

        If the ResultZipper runs in debug mode, only a directory at the given path will be created.

        :return: None
        """

        # Check for debug mode
        if self._is_debug:
            TaskHelper.create_directory(self._zip_path_final)
            return

        # Else, proceed with the normal operations

        TaskHelper.zip_dir(zip_path_running=self._zip_path_running, zip_path_final=self._zip_path_final,
                           dir_path=self._dir_path)
        TaskHelper.del_dir(self._dir_path)

        if self._error_occurred:
            self._task_progress_callback(self._task_id, TaskState.FINISHED_WITH_ERROR, 1)
        else:
            self._task_progress_callback(self._task_id, TaskState.FINISHED, 1)
