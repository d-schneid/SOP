import unittest

from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.Scheduler import Scheduler


class UnitTestDebugScheduler(unittest.TestCase):
    to_be_changed = False

    def test_work_is_done(self):
        Scheduler._instance = None
        Scheduler.default_scheduler = DebugScheduler
        sched = Scheduler.get_instance()
        sched.schedule(TestSched())
        self.assertTrue(UnitTestDebugScheduler.to_be_changed)  # add assertion here


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
        UnitTestDebugScheduler.to_be_changed = True
