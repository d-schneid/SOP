import django.test
from unittest import TestCase

from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler
from experiments.management.commands.dumpstatus import Command


class DumpStatusTests(django.test.TestCase):
    def test_dump_status(self):
        Scheduler._instance = UserRoundRobinScheduler()
        cmd = Command()
        with self.assertLogs(level="INFO") as cm:
            cmd.handle()
            self.assertIn("tasks", cm.output[0])
