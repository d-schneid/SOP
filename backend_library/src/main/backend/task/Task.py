import string

from collections.abc import Callable


class Task:

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable):
        self.user_id: int = user_id
        self.task_id: int = task_id
        self.task_progress_callback: Callable = task_progress_callback

    def schedule(self) -> None:
        return None
