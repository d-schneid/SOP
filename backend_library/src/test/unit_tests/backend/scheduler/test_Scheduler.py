import unittest

from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler


class UnitTestScheduler(unittest.TestCase):

    def setUp(self) -> None:
        Scheduler._instance = None
        Scheduler.default_scheduler = None

    def test_get_instance(self):
        with self.assertRaises(AssertionError):
            Scheduler.get_instance()
        Scheduler.default_scheduler = DebugScheduler
        dbg = Scheduler.get_instance()
        dbg2 = Scheduler.get_instance()
        self.assertEqual(dbg2, dbg)
        self.assertEqual(DebugScheduler, dbg.__class__)
        self.assertEqual(dbg, DebugScheduler.get_instance())

    def tearDown(self) -> None:
        self.setUp()

if __name__ == '__main__':
    unittest.main()
