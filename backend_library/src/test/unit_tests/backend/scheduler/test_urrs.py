import multiprocessing
import threading
import unittest
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
        self.assertEqual(None, sched.next_sched())  # add assertion here
        a = TestSched(-1, -1, 1)
        sched.schedule(a)
        b = TestSched(-1, -1, 0)
        sched.schedule(b)
        c = TestSched(-1, -1, 2)
        sched.schedule(c)
        self.assertEqual(c, sched.next_sched())
        self.assertEqual(a, sched.next_sched())
        self.assertEqual(b, sched.next_sched())
        self.assertEqual(None, sched.next_sched())

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
        tr4 = multiprocessing.Event()
        tbc5 = manager.Value('b', False)
        wait_for_subprocesses = multiprocessing.Event()
        wait_for_main = multiprocessing.Lock()
        with wait_for_main:
            urrs.schedule(TestSched(-1, 0, 0, None, tr4, wait_for_subprocesses, wait_for_main))
            urrs.schedule(TestSched(-1, 1, 0, tbc5, None, wait_for_subprocesses, wait_for_main))
            wait_for_subprocesses.wait(timeout)
            urrs.abort_by_task(1)
        self.assertTrue(tr4.wait(timeout))
        self.assertFalse(tbc5.value)

    def test_exec2(self):
        urrs = UserRoundRobinScheduler()
        tr6 = multiprocessing.Event()
        tbc7 = manager.Value('b', False)
        wait_for_subprocesses = multiprocessing.Event()
        wait_for_main = multiprocessing.Lock()
        with wait_for_main:
            for _ in range(multiprocessing.cpu_count()):
                urrs.schedule(TestSched(0, -1, 0, None, tr6, wait_for_subprocesses, wait_for_main))
                urrs.schedule(TestSched(1, -1, 0, tbc7, None, wait_for_subprocesses, wait_for_main))
            wait_for_subprocesses.wait(timeout)
            urrs.abort_by_user(1)
        self.assertTrue(tr6.wait(timeout))
        self.assertFalse(tbc7.value)

    def test_exec3(self):
        urrs = UserRoundRobinScheduler()
        tbc2 = multiprocessing.Event()
        tbc3 = multiprocessing.Event()
        wait_for_subprocesses = multiprocessing.Event()
        wait_for_main = multiprocessing.Lock()
        with wait_for_main:
            urrs.schedule(TestSched(-1, -1, 0, None, tbc2, wait_for_subprocesses, wait_for_main))
            wait_for_subprocesses.wait(timeout)
            urrs.graceful_shutdown(lambda: tbc3.set())
        self.assertTrue(tbc2.wait(timeout))
        self.assertTrue(tbc3.wait(timeout))
        self.assertTrue(urrs.is_shutting_down())

if __name__ == '__main__':
    unittest.main()


class TestSched(Schedulable):
    def __init__(self, uid, tid, prio, tbc=None, tr=None, set_before: multiprocessing.Event = None, wait_for=None):
        self.uid = uid
        self.tid = tid
        self.prio = prio
        self.tbc = tbc
        self.tr = tr
        self.set_before: multiprocessing.Event = set_before
        self.wait_for: threading.Lock = wait_for

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
