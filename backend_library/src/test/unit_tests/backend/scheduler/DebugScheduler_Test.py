import unittest

from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.Scheduler import Scheduler


class DebugSchedulerTest(unittest.TestCase):
    to_be_changed = False

    def test_work_is_done(self):
        Scheduler._instance = None
        sched = DebugScheduler()
        sched.schedule(TestSched())
        self.assertTrue(DebugSchedulerTest.to_be_changed)  # add assertion here


if __name__ == '__main__':
    unittest.main()


class TestSched(Schedulable):
    @property
    def user_id(self) -> int:
        return -1

    @property
    def task_id(self) -> int:
        return -1

    @property
    def priority(self) -> int:
        return 0

    def do_work(self) -> None:
        DebugSchedulerTest.to_be_changed = True
