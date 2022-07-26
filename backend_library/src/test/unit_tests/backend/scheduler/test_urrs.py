import time
import unittest
import multiprocessing
from multiprocessing import Manager
from multiprocessing.managers import SyncManager
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
        manager = Manager()
        tbc = manager.Value('b', False)

        Scheduler._instance = None
        urrs = UserRoundRobinScheduler()
        urrs.schedule(TestSched(-1, -1, 0, tbc))
        time.sleep(1)
        self.assertTrue(tbc.value)

        tbc4 = manager.Value('b', False)
        tbc5 = manager.Value('b', False)

        urrs.schedule(TestSched(-1, 0, 0, tbc4, 2))
        urrs.schedule(TestSched(-1, 1, 0, tbc5, 2))
        urrs.abort_by_task(1)
        time.sleep(4)
        self.assertTrue(tbc4.value)
        self.assertFalse(tbc5.value)

        tbc6 = manager.Value('b', False)
        tbc7 = manager.Value('b', False)
        for i in range(multiprocessing.cpu_count()):
            urrs.schedule(TestSched(0, -1, 0, tbc6, 2))
            urrs.schedule(TestSched(1, -1, 0, tbc7, 2))
        urrs.abort_by_user(1)
        time.sleep(4)
        self.assertTrue(tbc6.value)
        self.assertFalse(tbc7.value)

        tbc2 = manager.Value('b', False)
        tbc3 = manager.Value('b', False)

        urrs.schedule(TestSched(-1, -1, 0, tbc3, 2))
        urrs.graceful_shutdown(lambda: tbc2.set(True))
        time.sleep(4)
        self.assertTrue(tbc2.value)
        self.assertTrue(tbc3.value)
        self.assertTrue(urrs.is_shutting_down())

    def test_get_instance(self):
        Scheduler._instance = None
        urrs = UserRoundRobinScheduler.get_instance()
        self.assertEqual(UserRoundRobinScheduler, urrs.__class__)
        self.assertEqual(urrs, UserRoundRobinScheduler.get_instance())

if __name__ == '__main__':
    unittest.main()


class TestSched(Schedulable):
    def __init__(self, uid, tid, prio, tbc=None, sleep_dur=0):
        self.uid = uid
        self.tid = tid
        self.prio = prio
        self.tbc = tbc
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
        self.tbc.set(True)
