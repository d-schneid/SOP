import string

from collections.abc import Callable

class Task:
    user_id: string
    task_id: int
    progress_update_callback: Callable = None

    def __init__(self, user_id, task_id: int, progress_update_callback: Callable):
        self.user_id = user_id
        self.task_id = task_id
        self.progress_update_callback = progress_update_callback

    def schedule(self) -> None:
        return None
