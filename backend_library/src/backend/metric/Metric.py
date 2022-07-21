from abc import ABC

from backend.task.execution.core.Execution import Execution


class Metric(ABC):
    @staticmethod
    def compute_metric(execution: Execution, metric_result_path: str) -> None:
        """
        :param execution: The Execution to which this metric belongs to.
        :param metric_result_path: The path where the metric will store it's results to. Has to and with .csv
        :return: None
        """
        assert metric_result_path.endswith(".csv")
