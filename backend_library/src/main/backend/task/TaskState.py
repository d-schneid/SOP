from enum import Enum, auto


class TaskState(Enum):
    """
    Helper enum to convey information about a Task.
    """
    WAITING = auto, False, False, False
    RUNNING = auto, False, False, True
    RUNNING_WITH_ERROR = auto, False, True, True,
    FINISHED = auto, True, False, False
    FINISHED_WITH_ERROR = auto, True, True, False

    def is_finished(self) -> bool:
        """
        :return: True if the TaskState is finished, otherwise returns False.
        """
        return self.value[1]

    def error_occurred(self) -> bool:
        """
        :return: True if the TaskState has an error, otherwise returns False.
        """
        return self.value[2]

    def is_running(self) -> bool:
        """
        :return: True if the TaskState is running, otherwise returns False.
        """
        return self.value[3]
