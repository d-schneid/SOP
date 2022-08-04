import multiprocessing
import time
import unittest
from multiprocessing import Manager
from typing import Optional

from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler


class UserRoundRobinSchedulerMock(UserRoundRobinScheduler):

    def _UserRoundRobinScheduler__get_targeted_worker_count(self) -> int:
        return 0

    def next_sched(self) -> Optional[Schedulable]:
        return self._UserRoundRobinScheduler__get_next_schedulable()


class UnitTestUrrs(unittest.TestCase):

    def tearDown(self) -> None:
        Scheduler.get_instance().hard_shutdown()

    def test_priority(self):
        Scheduler._instance = None
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

        sched.schedule(TestSched(0, -1, 2))
        sched.schedule(TestSched(0, -1, 2))
        sched.schedule(TestSched(1, -1, 2))
        sched.schedule(TestSched(1, -1, 2))
        self.assertNotEqual(sched.next_sched().user_id, sched.next_sched().user_id)

    def test_exec(self):
        timeout = 10
        manager = Manager()
        tr = multiprocessing.Event()
        Scheduler._instance = None
        urrs = UserRoundRobinScheduler()
        urrs.schedule(TestSched(-1, -1, 0, None, tr))
        self.assertTrue(tr.wait(timeout))

        tr4 = multiprocessing.Event()
        tbc5 = manager.Value('b', False)
        urrs.schedule(TestSched(-1, 0, 0, None, tr4, 1))
        urrs.schedule(TestSched(-1, 1, 0, tbc5, None, 3))
        urrs.abort_by_task(1)
        self.assertTrue(tr4.wait(timeout))
        time.sleep(3)
        self.assertFalse(tbc5.value)

        tr6 = multiprocessing.Event()
        tbc7 = manager.Value('b', False)
        for _ in range(multiprocessing.cpu_count()):
            urrs.schedule(TestSched(0, -1, 0, None, tr6, 1))
            urrs.schedule(TestSched(1, -1, 0, tbc7, None, 3))
        urrs.abort_by_user(1)
        self.assertTrue(tr6.wait(timeout))
        time.sleep(3)
        self.assertFalse(tbc7.value)

        tbc2 = multiprocessing.Event()
        tbc3 = multiprocessing.Event()
        urrs.schedule(TestSched(-1, -1, 0, None, tbc2, 6))
        time.sleep(3)
        urrs.graceful_shutdown(lambda: tbc3.set())
        self.assertTrue(tbc2.wait(timeout))
        self.assertTrue(tbc3.wait(timeout))
        self.assertTrue(urrs.is_shutting_down())

    def test_get_instance(self):
        Scheduler._instance = None
        urrs = UserRoundRobinScheduler()
        urrs = Scheduler.get_instance()
        self.assertEqual(UserRoundRobinScheduler, urrs.__class__)
        self.assertEqual(urrs, UserRoundRobinScheduler.get_instance())

if __name__ == '__main__':
    unittest.main()


class TestSched(Schedulable):
    def __init__(self, uid, tid, prio, tbc=None, tr=None, sleep_dur=0):
        self.uid = uid
        self.tid = tid
        self.prio = prio
        self.tbc = tbc
        self.tr = tr
        self.slp_dur = sleep_dur

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
        time.sleep(self.slp_dur)
        if self.tbc is not None:
            self.tbc.set(True)
        if self.tr is not None:
            self.tr.set()
