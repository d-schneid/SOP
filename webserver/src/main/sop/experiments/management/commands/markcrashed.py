from typing import Any, Optional

from django.core.management.base import BaseCommand

from experiments.models.managers import ExecutionManager


class Command(BaseCommand):
    help = "Marks all executions that are marked as running"

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        self.stdout.write("Marking running executions as crashed...", ending="")
        self.stdout.flush()
        ExecutionManager.mark_running_executions_as_crashed()
        self.stdout.write(self.style.SUCCESS(" OK"))
        return None
