import time
import unittest
from multiprocessing import Manager
from typing import Optional
from unittest import skip

from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler


class UserRoundRobinSchedulerMock(UserRoundRobinScheduler):

    def _UserRoundRobinScheduler__get_targeted_worker_count(self) -> int:
        return 0

    def next_sched(self) -> Optional[Schedulable]:
        return self._UserRoundRobinScheduler__get_next_schedulable()


class UnitTestUrrs(unittest.TestCase):
    to_be_changed = Manager().Value('b', False)

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
        Scheduler._instance = None
        urss = UserRoundRobinScheduler()
        urss.schedule(TestSched(-1, -1, 0))
        time.sleep(2)
        self.assertTrue(UnitTestUrrs.to_be_changed.value)


if __name__ == '__main__':
    unittest.main()


class TestSched(Schedulable):
    def __init__(self, uid, tid, prio):
        self.uid = uid
        self.tid = tid
        self.prio = prio

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
        UnitTestUrrs.to_be_changed.set(True)
