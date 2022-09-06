from typing import Optional

from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler


class UrrsWoWorkers(UserRoundRobinScheduler):

    def _get_targeted_worker_count(self) -> int:
        return 0

    def next_sched(self) -> Optional[Schedulable]:
        return self._get_next_schedulable()
