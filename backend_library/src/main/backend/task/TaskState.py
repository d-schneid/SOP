from enum import Enum, auto


class TaskState(Enum):
    WAITING = auto, False, False
    RUNNING = auto, False, False
    RUNNING_WITH_ERROR = auto, False, True
    FINISHED = auto, True, False
    FINISHED_WITH_ERROR = auto, True, True

    def is_finished(self) -> bool:
        return self.value[1]

    def error_occurred(self) -> bool:
        return self.value[2]
