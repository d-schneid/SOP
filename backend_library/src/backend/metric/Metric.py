from abc import ABC, abstractmethod

from backend.metric.ExecutionElementMetricHelper \
    import ExecutionElementMetricHelper as eem_helper


class Metric(ABC):
    _eem_helper = eem_helper()

    @staticmethod
    @abstractmethod
    def compute_metric(metric_result_path: str,
                       algorithm_directory_paths: list[str]) -> None:
        """
        :param metric_result_path: The path where the metric will store its results to.
        Has to and with .csv
        :param algorithm_directory_paths: A list which contains all the paths
        to the folder of the selected algorithms.
        (Use the build in property algorithm_directory_paths in Execution)
        :return: None
        """
        assert metric_result_path.endswith(".csv")

    @property
    def eem_helper(self) -> eem_helper:
        """
        :return: The ExecutionElementMetricHelper used by this metric
        (allows the child classes to access it)
        """
        return self._eem_helper
