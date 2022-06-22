from enum import Enum, auto


class TaskState(Enum):
    WAITING = auto, False, False, False
    RUNNING = auto, False, False, True
    RUNNING_WITH_ERROR = auto, False, True, True,
    FINISHED = auto, True, False, False
    FINISHED_WITH_ERROR = auto, True, True, False

    def is_finished(self) -> bool:
        return self.value[1]

    def error_occurred(self) -> bool:
        return self.value[2]

    def is_running(self) -> bool:
        return self.value[3]
