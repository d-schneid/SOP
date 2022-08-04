from abc import ABC, abstractmethod
from typing import Optional


class Schedulable(ABC):
    """Abstract class for work units that can be scheduled using a scheduler"""

    @property
    @abstractmethod
    def user_id(self) -> int:
        """The id of the user this Schedulable belongs to, has to be >=-1,
         where -1 indicates that the Schedulable belongs to no user"""
        pass

    @property
    @abstractmethod
    def task_id(self) -> int:
        """The id of the task this Schedulable belongs to, has to be >=-1,
         where -1 indicates that the Schedulable belongs to no task"""
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """The priority of this Schedulable, between 0 and 100 (both inclusive)"""
        pass

    def run_before_on_main(self) -> None:
        """
        Is executed before the do_work function on the main Process.
        This method may or may not be executed on an extra thread of the main Process.
        Should not be to CPU-heavy because of this.
        """
        return None

    @abstractmethod
    def do_work(self) -> Optional[int]:
        """
        The main work function of this Schedulable, may be executed
        a) on the main thread
        b) on an extra thread of the main process
        c) in an extra process, if created after run_before_on_main using fork
        :return: Optionally an integer status provided to the run_later_on_main function
        """
        return None

    def run_later_on_main(self, statuscode: int) -> None:
        """
        Executed after do_work finished on the main Process.
        This method may or may not be executed on an extra thread of the main Process.
        :param statuscode: The statuscode provided by do_work,
         depending on the python implementation,
          only the last 8/16/32 bit might be transferred.
         If do_work returned None no assumptions about this parameter are to be made
        """
        return None
