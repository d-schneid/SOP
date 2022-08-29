import multiprocessing
import unittest
from multiprocessing.managers import ValueProxy

from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler
from test.unit_tests.backend.scheduler.SchedulableForTesting import TestSched


class UnitTestDebugScheduler(unittest.TestCase):

    def setUp(self) -> None:
        Scheduler._instance = None

    def test_functionality(self):
        scheduler = DebugScheduler()
        self.assertFalse(scheduler.is_shutting_down())
        with multiprocessing.Manager() as m:
            toChange: ValueProxy[bool] = m.Value('b', False)
            sched = TestSched(-1, -1, 0, toChange)
            scheduler.schedule(sched)
            self.assertTrue(toChange.get())
        self.assertIsNone(scheduler.hard_shutdown())

    def tearDown(self) -> None:
        self.setUp()


if __name__ == '__main__':
    unittest.main()
