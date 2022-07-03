from abc import ABC, abstractmethod


class Schedulable(ABC):
    @property
    @abstractmethod
    def user_id(self) -> int:
        return -1

    @property
    @abstractmethod
    def task_id(self) -> int:
        return -1

    @property
    @abstractmethod
    def priority(self) -> int:
        return 0

    @abstractmethod
    def do_work(self) -> None:
        return None
