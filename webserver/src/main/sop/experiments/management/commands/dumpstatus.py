from typing import Optional, Any

from django.core.management.base import BaseCommand
from backend.scheduler.Scheduler import Scheduler


class Command(BaseCommand):
    help = "Logs running backend task status."

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        Scheduler.get_instance().log_debug_data()
        return None
