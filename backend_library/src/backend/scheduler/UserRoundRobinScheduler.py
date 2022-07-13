import heapq
import itertools
import multiprocessing
import sys
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from multiprocessing import Condition, Process
from multiprocessing.process import BaseProcess
from threading import Thread
from typing import Callable, Optional, Dict, List, Tuple

from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.Scheduler import Scheduler


class UserRoundRobinScheduler(Scheduler):
    def __init__(self):
        super().__init__()
        self.__shutdown_ongoing: bool = False
        self.__on_shutdown_completed: Optional[Callable] = None
        self.__empty_queue: Condition = Condition()
        self.__threads: List[Thread] = list()
        self.__user_queues: OrderedDict[int, List[PrioritizedSchedulable]] \
            = OrderedDict()
        self.__next_queue: int = -1
        self.__running: Dict[Schedulable, Tuple[Process, bool]] = dict()
        for i in range(self.__get_targeted_worker_count()):
            self.__make_worker_thread()

    def __make_worker_thread(self):
        t = Thread(
            target=UserRoundRobinScheduler.__thread_main,
            args=(self,))
        self.__threads.append(t)
        t.start()

    def abort_by_task(self, task_id: int) -> None:
        self.__abort(lambda x: x.task_id == task_id)

    def abort_by_user(self, user_id: int) -> None:
        self.__abort(lambda x: x.user_id == user_id)

    def __abort(self, selector: Callable[[Schedulable], bool]):
        with self.__empty_queue:
            for _, q in self.__user_queues.values():
                for i in range(len(q)):
                    if selector(q[i]):
                        # there is no way to delete nicely from python heapqs
                        q[i] = q[-1]
                        q.pop()
            for k, v in self.__running:
                if selector(k):
                    self.__running[k] = (v[0], True)
                    v[0].terminate()

    def hard_shutdown(self) -> None:
        self.__on_shutdown_completed = None
        self.__shutdown_ongoing = True
        for k, v in self.__running.items():
            self.__running[k] = (v[0], True)
            v[0].terminate()

    def graceful_shutdown(self,
                          on_shutdown_completed: Optional[Callable] = None) -> None:
        with self.__empty_queue:
            self.__shutdown_ongoing = True
            self.__on_shutdown_completed = on_shutdown_completed
            self.__user_queues = OrderedDict()
            self.__empty_queue.notify_all()

    def is_shutting_down(self) -> bool:
        return self.__shutdown_ongoing

    def schedule(self, to_schedule: Schedulable) -> None:
        uid = to_schedule.user_id
        assert uid >= -1
        tid = to_schedule.task_id
        assert tid >= -1
        priority = to_schedule.priority
        assert 0 <= priority <= 100
        with self.__empty_queue:
            if uid not in self.__user_queues:
                self.__next_queue = len(self.__user_queues)
                self.__user_queues[uid] = []
            prioritized_schedulable = PrioritizedSchedulable(to_schedule, priority)
            heapq.heappush(self.__user_queues[uid], prioritized_schedulable)
            self.__empty_queue.notify()

    def __process_main(self, sched: Schedulable):
        r = sched.do_work()
        if r is None:
            r = 0
        sys.exit(r)

    def __thread_main(self) -> None:
        while not self.__shutdown_ongoing:
            with self.__empty_queue:
                next_sched = self.__get_next_schedulable()
                while next_sched is None:
                    self.__empty_queue.wait()
                    next_sched = self.__get_next_schedulable()
                    if self.__shutdown_ongoing:
                        self.__handle_graceful_shutdown()
                        return
                p = Process(target=UserRoundRobinScheduler.__process_main,
                            args=(self, next_sched,))
                self.__running[next_sched] = (p, False)
                p.start()
            p.join()
            if self.hard_shutdown():
                if not self.__running[next_sched][1]:
                    next_sched.run_later_on_main(p.exitcode)
        self.__handle_graceful_shutdown()

    def __handle_graceful_shutdown(self) -> None:
        if self.__on_shutdown_completed is not None:
            with self.__empty_queue:
                self.__threads.remove(threading.current_thread())
                if len(self.__threads) == 0:
                    self.__on_shutdown_completed()

    def __get_next_schedulable(self) -> Optional[Schedulable]:
        if self.__next_queue == -1:
            return None
        queues_after_current = \
            itertools.islice(self.__user_queues.items(), self.__next_queue, None)
        queues_before_current = \
            itertools.islice(self.__user_queues.items(), self.__next_queue)
        ordered_queues = itertools.chain(queues_after_current, queues_before_current)
        for k, v in ordered_queues:
            self.__next_queue = self.__next_queue + 1
            if len(v) > 0:
                self.__next_queue = self.__next_queue % len(self.__user_queues)
                return heapq.heappop(v).schedulable
        return None

    def __get_targeted_worker_count(self) -> int:
        return multiprocessing.cpu_count() * 2


@dataclass(order=True)
class PrioritizedSchedulable:
    priority: int
    schedulable: Schedulable = field(compare=False)

    def __init__(self, sched: Schedulable, prio: int):
        self.priority = -prio
        self.schedulable = sched
