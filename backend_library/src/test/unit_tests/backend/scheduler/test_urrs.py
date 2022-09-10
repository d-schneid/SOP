import multiprocessing
import unittest
from multiprocessing import Manager

from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler
from test.UrrsWoWorkers import UrrsWoWorkers
from test.unit_tests.backend.scheduler.SchedulableForTesting import TestSched

timeout = 60
manager = Manager()


class PriorityTests(unittest.TestCase):
    def setUp(self) -> None:
        Scheduler._instance = None

    def test_priorities(self):
        sched = UrrsWoWorkers()
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

    def test_round_robin_scheduling(self):
        sched = UrrsWoWorkers()

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

    def test_abort_by_task(self):
        urrs = UserRoundRobinScheduler()
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

    def test_basic_exec(self):
        urrs = UserRoundRobinScheduler()
        tr = multiprocessing.Event()
        urrs.schedule(TestSched(-1, -1, 0, None, tr))
        self.assertTrue(tr.wait(timeout))

    def test_multi_abort_by_user(self):
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

    def test_graceful_shutdown(self):
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

    def test_shutdown_before_schedule(self):
        # Tests race condition handling in the 3rd to 5th line of URRS._run_schedulable
        urrs = UserRoundRobinScheduler()
        tbc = manager.Value('b', False)
        urrs.graceful_shutdown()
        urrs._run_single(
            TestSched(1, -1, 0, tbc))
        self.assertFalse(tbc.value)


if __name__ == '__main__':
    unittest.main()
