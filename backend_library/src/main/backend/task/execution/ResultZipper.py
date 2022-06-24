import string
from typing import Callable

from backend_library.src.main.backend.scheduler.Schedulable import Schedulable


class ResultZipper(Schedulable):
    def __init__(self, user_id: int, task_id: int, error_occurred: bool,
                 task_progress_callback: Callable,  path_to_zip: string, zipped_file_path: string):
        self.user_id: int = user_id
        self.task_id: int = task_id
        self.error_occurred: bool = error_occurred
        self.task_progress_callback: Callable = task_progress_callback
        self.path_to_zip: string = path_to_zip
        self.zipped_file_path: string = zipped_file_path

    def get_user_id(self) -> int:
        return self.user_id

    def get_task_id(self) -> int:
        return self.task_id

    def do_work(self) -> None:
        return None
