from abc import ABC

from backend.task.execution.core.Execution import Execution
from backend.metric.ExecutionElementMetricHelper import ExecutionElementMetricHelper as eem_helper


class Metric(ABC):
    _eem_helper = eem_helper()

    @staticmethod
    def compute_metric(execution: Execution, metric_result_path: str) -> None:
        """
        :param execution: The Execution to which this metric belongs to.
        :param metric_result_path: The path where the metric will store it's results to. Has to and with .csv
        :return: None
        """
        assert metric_result_path.endswith(".csv")

    @property
    def eem_helper(self) -> eem_helper:
        return self._eem_helper
