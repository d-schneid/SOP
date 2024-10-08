import heapq
import itertools
import multiprocessing
import sys
import threading
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from logging import info, debug, critical
from multiprocessing import Condition, Process, synchronize
from threading import Thread
from typing import Optional

from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.Scheduler import Scheduler


class UserRoundRobinScheduler(Scheduler):
    """Scheduler that schedules round-robin by user id
    with priorities within the user queues,
    supports abort_by_user, abort_by_task and graceful_shutdown"""

    def __init__(self):
        super().__init__()
        UserRoundRobinScheduler.__start_by_fork()
        try:
            # When the fork happens whilst the resource tracker threading-lock is held,
            # the lock will never be released in the subprocess.
            # If that subprocess then tries to acquire the lock itself,
            # it will be stuck there indefinitely.
            # (see `man fork`)
            # one could create a new lock in subprocesses,
            # but that could result in two resource trackers existing.
            # Instead replace the lock initially with a multiprocessing.Lock,
            # which might be a bit slower but is the (only?) safe solution

            # internal cpython classes,
            # so ignore code checkers not resolving these references
            # noinspection PyUnresolvedReferences
            import multiprocessing.resource_tracker
            # noinspection PyProtectedMember,PyUnresolvedReferences
            tracker = multiprocessing.resource_tracker._resource_tracker
            # can not use isinstance as thread.Lock is an alias
            if tracker._lock.__class__ == threading.Lock().__class__:
                tracker._lock = multiprocessing.Lock()
        except (AttributeError, ImportError):
            # Running on an interpreter without shitty resource tracker
            # => nothing to worry about
            pass
        self.__shutdown_ongoing: bool = False
        self.__on_shutdown_completed: Optional[Callable[[], None]] = None
        self.__empty_queue: synchronize.Condition = Condition()
        self.__threads: set[Thread] = set()
        self.__user_queues: OrderedDict[int, list[PrioritizedSchedulable]] \
            = OrderedDict()
        self.__next_queue: int = -1
        self.__running: dict[Schedulable, tuple[Process, bool]] = dict()
        count = self._get_targeted_worker_count()
        debug(f"starting urrs with {count} workers")
        for i in range(count):
            self.__make_worker_thread()

    @staticmethod
    def __start_by_fork():
        """Ensures that the process starting method is fork"""
        assert "fork" in multiprocessing.get_all_start_methods(), \
            "Multiprocessing will not work under native windows use linux"
        if multiprocessing.get_start_method(True) is None:
            multiprocessing.set_start_method("fork")
        assert multiprocessing.get_start_method(True) == "fork", \
            "apparently the setting the start method of processes was not possible"

    def __make_worker_thread(self):
        """Creates a new supervisor thread"""
        t = Thread(
            target=UserRoundRobinScheduler.__thread_main,
            args=(self,), daemon=True)
        self.__threads.add(t)
        t.start()

    def abort_by_task(self, task_id: int) -> None:
        self.__abort(lambda x: x.task_id == task_id)

    def abort_by_user(self, user_id: int) -> None:
        self.__abort(lambda x: x.user_id == user_id)

    def log_debug_data(self):
        info(f"[{datetime.now()}] Printing currently registered tasks:")
        with self.__empty_queue:
            for running in self.__running.items():
                info(f"{running[0]} is registered as running on PID {running[1][0].pid}"
                     f" is alive returns {running[1][0].is_alive()}")
            for q in self.__user_queues.values():
                for ps in q:
                    info(f"{ps.schedulable} is waiting in queue")

    def __abort(self, selector: Callable[[Schedulable], bool]):
        """Aborts all Tasks matching the selector provided"""
        with self.__empty_queue:
            for _, q in self.__user_queues.items():
                i = 0
                while i < len(q):
                    if selector(q[i].schedulable):
                        # there is no way to delete nicely from python heapqs
                        q[i].schedulable.run_later_on_main(None)
                        q[i] = q[-1]
                        q.pop()
                        heapq.heapify(q)
                    else:
                        i = i + 1
            for k, v in self.__running.items():
                if selector(k) and not v[1]:
                    self.__running[k] = (v[0], True)
                    try:
                        v[0].kill()
                    except AttributeError:
                        # Has just stopped, ignore
                        pass

    def hard_shutdown(self) -> None:
        critical("hard shutdown of urrs requested")
        with self.__empty_queue:
            self.__on_shutdown_completed = None
            self.__shutdown_ongoing = True
            self.__abort(lambda _: True)
            self.__empty_queue.notify_all()

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
        if priority == 100:
            t = Thread(
                target=UserRoundRobinScheduler._run_single,
                args=(self, to_schedule), daemon=True)
            self.__threads.add(t)
            t.start()
            return
        with self.__empty_queue:
            if uid not in self.__user_queues:
                self.__next_queue = len(self.__user_queues)
                self.__user_queues[uid] = []
            prioritized_schedulable = PrioritizedSchedulable(to_schedule, priority)
            heapq.heappush(self.__user_queues[uid], prioritized_schedulable)
            self.__empty_queue.notify()

    def _run_single(self, sched: Schedulable):
        self._run_schedulable(lambda: sched)
        self.__threads.discard(threading.current_thread())

    def __process_main(self, sched: Schedulable):
        """main method executed by worker processes,
         just runs a schedulable and dies with it's statuscode"""
        # No coverage of this method is recorded as extra processes are not recorded,
        # and an extra unittest of this method is not possible,
        # as it would also exit the unittest process

        r = sched.do_work()
        sys.exit(0 if r is None else r)

    def __thread_main(self) -> None:
        """main method executed by supervisor threads,
        starts worker processes when schedulables are available"""
        while not self.__shutdown_ongoing:
            if self._run_schedulable(self._get_next_schedulable):
                break
        self.__handle_shutdown()

    def __handle_shutdown(self) -> None:
        """Handles a graceful shutdown when detected"""
        if self.__on_shutdown_completed is not None:
            with self.__empty_queue:
                self.__threads.discard(threading.current_thread())
                if len(self.__threads) == 0:
                    self.__on_shutdown_completed()

    def _get_next_schedulable(self) -> Optional[Schedulable]:
        """Retrieves the next schedulable to run, to be run within __empty_queue only"""
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

    def _get_targeted_worker_count(self) -> int:
        """Calculates the number of worker threads to use"""
        return multiprocessing.cpu_count()

    def _run_schedulable(self, sched_src: Callable[[], Schedulable]) -> bool:
        with self.__empty_queue:
            next_sched = sched_src()
            if self.__shutdown_ongoing:
                self.__handle_shutdown()
                return True
            while next_sched is None:
                self.__empty_queue.wait()
                next_sched = self._get_next_schedulable()
                if self.__shutdown_ongoing:
                    self.__handle_shutdown()
                    return True
            p = Process(target=UserRoundRobinScheduler.__process_main,
                        args=(self, next_sched,), daemon=True)
            self.__running[next_sched] = (p, False)
        debug(f"preparing to run {next_sched} (prio: {next_sched.priority})")
        next_sched.run_before_on_main()
        with self.__empty_queue:
            if self.__shutdown_ongoing:
                next_sched.run_later_on_main(None)
                self.__handle_shutdown()
                return True
            if self.__running[next_sched][1]:
                next_sched.run_later_on_main(None)
                return False
            info(f"{next_sched} will now be started")
            p.start()
        p.join()
        debug(f"running cleanup for {next_sched}")
        if self.__running[next_sched][1]:
            with self.__empty_queue:
                next_sched.run_later_on_main(None)
        else:
            next_sched.run_later_on_main(p.exitcode)
        self.__running.pop(next_sched)
        debug(f"done with {next_sched}")
        return False


@dataclass(order=True)
class PrioritizedSchedulable:
    """dataclass for ordering schedulables by priority"""
    priority: int
    schedulable: Schedulable = field(compare=False)

    def __init__(self, sched: Schedulable, prio: int):
        self.priority = -prio
        self.schedulable = sched
