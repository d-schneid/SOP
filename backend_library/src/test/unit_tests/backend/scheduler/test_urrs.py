import multiprocessing
import threading
import unittest
from collections.abc import Callable
from multiprocessing import Manager
from typing import Optional

from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler

timeout = 60
manager = Manager()


class UserRoundRobinSchedulerMock(UserRoundRobinScheduler):

    def _UserRoundRobinScheduler__get_targeted_worker_count(self) -> int:
        return 0

    def next_sched(self) -> Optional[Schedulable]:
        return self._UserRoundRobinScheduler__get_next_schedulable()


class PriorityTests(unittest.TestCase):
    def setUp(self) -> None:
        Scheduler._instance = None

    def test_priority1(self):
        sched = UserRoundRobinSchedulerMock()
        self.assertIsNone(sched.next_sched())  # add assertion here
        a = TestSched(-1, -1, 1)
        sched.schedule(a)
        b = TestSched(-1, -1, 0)
        sched.schedule(b)
        c = TestSched(-1, -1, 2)
        sched.schedule(c)
        self.assertEqual(c, sched.next_sched())
        self.assertEqual(a, sched.next_sched())
        self.assertEqual(b, sched.next_sched())
        self.assertIsNone(sched.next_sched())

    def test_priority2(self):
        sched = UserRoundRobinSchedulerMock()

        sched.schedule(TestSched(0, -1, 2))
        sched.schedule(TestSched(0, -1, 2))
        sched.schedule(TestSched(1, -1, 2))
        sched.schedule(TestSched(1, -1, 2))
        self.assertNotEqual(sched.next_sched().user_id, sched.next_sched().user_id)

    def tearDown(self) -> None:
        Scheduler.get_instance().hard_shutdown()
        Scheduler._instance = None


class UnitTestUrrs(unittest.TestCase):
    def setUp(self) -> None:
        Scheduler._instance = None

    def tearDown(self) -> None:
        Scheduler.get_instance().hard_shutdown()
        Scheduler._instance = None

    def test_exec(self):
        urrs = UserRoundRobinScheduler()
        tr = multiprocessing.Event()

        urrs.schedule(TestSched(-1, -1, 0, None, tr))
        self.assertTrue(tr.wait(timeout))
        ts = multiprocessing.Event()
        tbc = manager.Value('b', False)
        wait_for_sub = multiprocessing.Event()
        wait_for_main = multiprocessing.Lock()
        with wait_for_main:
            urrs.schedule(TestSched(-1, 0, 0, None, ts, wait_for_sub, wait_for_main))
            urrs.schedule(TestSched(-1, 1, 0, tbc, None, wait_for_sub, wait_for_main))
            wait_for_sub.wait(timeout)
            urrs.abort_by_task(1)
        self.assertTrue(ts.wait(timeout))
        self.assertFalse(tbc.value)

    def test_exec2(self):
        urrs = UserRoundRobinScheduler()
        ts = multiprocessing.Event()
        tbc = manager.Value('b', False)
        wait_for_sub = multiprocessing.Event()
        wait_for_main = multiprocessing.Lock()
        with wait_for_main:
            for _ in range(multiprocessing.cpu_count()):
                urrs.schedule(
                    TestSched(0, -1, 0, None, ts, wait_for_sub, wait_for_main))
                urrs.schedule(
                    TestSched(1, -1, 0, tbc, None, wait_for_sub, wait_for_main))
            wait_for_sub.wait(timeout)
            urrs.abort_by_user(1)
        self.assertTrue(ts.wait(timeout))
        self.assertFalse(tbc.value)

    def test_exec3(self):
        urrs = UserRoundRobinScheduler()
        ts = multiprocessing.Event()
        ts_by_shutdown = multiprocessing.Event()
        wait_for_sub = multiprocessing.Event()
        wait_for_main = multiprocessing.Lock()
        with wait_for_main:
            urrs.schedule(TestSched(-1, -1, 0, None, ts, wait_for_sub, wait_for_main))
            wait_for_sub.wait(timeout)
            urrs.graceful_shutdown(lambda: ts_by_shutdown.set())
        self.assertTrue(ts.wait(timeout))
        self.assertTrue(ts_by_shutdown.wait(timeout))
        self.assertTrue(urrs.is_shutting_down())

    def test_abort_while_exec(self):
        urrs = UserRoundRobinScheduler()
        tbc = manager.Value('b', False)
        ts = multiprocessing.Event()
        urrs.schedule(
            TestSched(1, -1, 0, tbc, run_before=lambda: urrs.abort_by_user(1),
                      run_after=lambda status: ts.set() if status is None else None))
        self.assertTrue(ts.wait(timeout))
        self.assertFalse(tbc.value)

    def test_shutdown_while_exec(self):
        urrs = UserRoundRobinScheduler()
        tbc = manager.Value('b', False)
        ts = multiprocessing.Event()
        ts_shut = multiprocessing.Event()
        urrs.schedule(
            TestSched(1, -1, 0, tbc,
                      run_before=lambda: urrs.graceful_shutdown(lambda: ts_shut.set()),
                      run_after=lambda status: ts.set() if status is None else None))
        self.assertTrue(ts.wait(timeout))
        self.assertTrue(ts_shut.wait(timeout))
        self.assertFalse(tbc.value)


if __name__ == '__main__':
    unittest.main()


class TestSched(Schedulable):
    def __init__(self, uid, tid, prio, tbc=None, tr=None,
                 set_before: multiprocessing.Event = None, wait_for=None,
                 run_before: Optional[Callable] = None,
                 run_after: Optional[Callable[[Optional[int]], None]] = None):
        self.uid = uid
        self.tid = tid
        self.prio = prio
        self.tbc = tbc
        self.tr = tr
        self.set_before: multiprocessing.Event = set_before
        self.wait_for: threading.Lock = wait_for
        self.run_before = run_before
        self.run_after = run_after

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
        if self.tr is not None:
            self.tr.set()

    def run_before_on_main(self) -> None:
        if self.run_before is not None:
            self.run_before()

    def run_later_on_main(self, statuscode: Optional[int]) -> None:
        if self.run_after is not None:
            self.run_after(statuscode)
