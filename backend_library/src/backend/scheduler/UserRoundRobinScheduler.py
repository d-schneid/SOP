import heapq
import itertools
import multiprocessing
import sys
from collections import OrderedDict
from dataclasses import dataclass, field
from multiprocessing import Condition, Process
from multiprocessing.process import BaseProcess
from typing import Callable, Optional, Dict, List

from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.Scheduler import Scheduler


class UserRoundRobinScheduler(Scheduler):
    def __init__(self):
        super().__init__()
        self.__graceful_shutdown_ongoing: bool = False
        self.__on_shutdown_completed: Optional[Callable] = None
        self.__empty_queue: Condition = Condition()
        self.__workers: Dict[BaseProcess, Optional[Schedulable]] = dict()
        self.__user_queues: OrderedDict[int, List[PrioritizedSchedulable]] \
            = OrderedDict()
        self.__next_queue: int = -1
        for i in range(UserRoundRobinScheduler.__get_targeted_worker_count()):
            self.__make_worker()

    def __make_worker(self):
        p = Process(
            target=UserRoundRobinScheduler._UserRoundRobinScheduler__worker_main,
            args=(self,))
        self.__workers[p] = None
        p.start()

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
            for k, v in self.__user_queues:
                if selector(v):
                    k.terminate()
                    self.__workers.pop(k)
                    self.__make_worker()

    def hard_shutdown(self) -> None:
        for p in self.__workers.keys():
            p.terminate()

    def graceful_shutdown(self,
                          on_shutdown_completed: Optional[Callable] = None) -> None:
        with self.__empty_queue:
            self.__graceful_shutdown_ongoing = True
            self.__on_shutdown_completed = on_shutdown_completed
            for k, v in self.__workers.items():
                if v is None:
                    k.terminate()
                    self.__workers.pop(k)
            if len(self.__workers) == 0 and on_shutdown_completed is not None:
                on_shutdown_completed()

    def is_shutting_down(self) -> bool:
        return self.__graceful_shutdown_ongoing

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

    def __worker_main(self) -> None:
        while not self.__graceful_shutdown_ongoing:
            with self.__empty_queue:
                next_sched: Optional[Schedulable] = self.__get_next_schedulable()
                while next_sched is None:
                    self.__empty_queue.wait()
                    next_sched = self.__get_next_schedulable()
                    self.__check_for_graceful_shutdown()
                self.__workers[multiprocessing.current_process()] = next_sched
            next_sched.do_work()
            self.__workers[multiprocessing.current_process()] = None
        self.__check_for_graceful_shutdown()

    def __check_for_graceful_shutdown(self) -> None:
        if self.__graceful_shutdown_ongoing:
            if self.__on_shutdown_completed is not None:
                with self.__empty_queue:
                    self.__workers.pop(multiprocessing.current_process())
                    if len(self.__workers) == 0:
                        self.__on_shutdown_completed()
            sys.exit()
        else:
            return None

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
