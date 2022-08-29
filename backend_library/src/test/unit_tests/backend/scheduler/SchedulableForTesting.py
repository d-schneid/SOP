import multiprocessing
from multiprocessing.managers import ValueProxy
from typing import Optional, Callable

from backend.scheduler.Schedulable import Schedulable

timeout = 60


class TestSched(Schedulable):
    def __init__(self, uid: int = -1, tid: int = -1, prio: int = 0,
                 tbc: Optional[ValueProxy[bool]] = None,
                 set_last: Optional[multiprocessing.Event] = None,
                 set_before: Optional[multiprocessing.Event] = None,
                 wait_for: Optional[multiprocessing.Lock] = None,
                 run_before: Optional[Callable[[], None]] = None,
                 run_after: Optional[Callable[[Optional[int]], None]] = None):
        self.uid: int = uid
        self.tid: int = tid
        self.prio: int = prio
        self.tbc: Optional[ValueProxy[bool]] = tbc
        self.set_last: Optional[multiprocessing.Event] = set_last
        self.set_before: Optional[multiprocessing.Event] = set_before
        self.wait_for: Optional[multiprocessing.Lock] = wait_for
        self.run_before: Optional[Callable[[], None]] = run_before
        self.run_after: Optional[Callable[[Optional[int]], None]] = run_after

    @property
    def user_id(self) -> int:
        return self.uid

    @property
    def task_id(self) -> int:
        return self.tid

    @property
    def priority(self) -> int:
        return self.prio

    def do_work(self) -> None:
        if self.set_before is not None:
            self.set_before.set()
        if self.wait_for is not None:
            self.wait_for.acquire(True, timeout)
            self.wait_for.release()
        if self.tbc is not None:
            self.tbc.set(True)
        if self.set_last is not None:
            self.set_last.set()

    def run_before_on_main(self) -> None:
        if self.run_before is not None:
            self.run_before()

    def run_later_on_main(self, statuscode: Optional[int]) -> None:
        if self.run_after is not None:
            self.run_after(statuscode)
