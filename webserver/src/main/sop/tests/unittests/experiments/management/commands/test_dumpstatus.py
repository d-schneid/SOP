import django.test
from django.urls import reverse

from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler


class DumpStatusTests(django.test.TestCase):
    def test_dump_status(self):
        Scheduler._instance = UserRoundRobinScheduler()
        with self.assertLogs(level="INFO") as cm:
            self.client.get(reverse("request_scheduler_dump"))
            self.assertIn("tasks", cm.output[0])
