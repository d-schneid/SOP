import string

from collections.abc import Callable


class Task:
    user_id: string
    task_id: int
    task_progress_callback: Callable = None

    def __init__(self, user_id, task_id: int, task_progress_callback: Callable):
        self.user_id = user_id
        self.task_id = task_id
        self.task_progress_callback = task_progress_callback

    def schedule(self) -> None:
        return None
