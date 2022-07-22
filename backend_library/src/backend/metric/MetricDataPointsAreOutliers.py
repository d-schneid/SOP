from abc import ABC

import numpy as np

from backend.metric.Metric import Metric
from backend.task.execution.core.Execution import Execution
from backend.metric.ExecutionElementMetricHelper import ExecutionElementMetricHelper as eem_helper


class MetricDataPointsAreOutliers(ABC, Metric):

    @staticmethod
    def compute_metric(execution: Execution, metric_result_path: str) -> None:
        """
        :param execution: The Execution to which this metric belongs to.
        :param metric_result_path: The path where the metric will store its results to. Has to end with .csv
        :return: None
        """
        assert metric_result_path.endswith(".csv")

        execution_result_path: list[str] = eem_helper. \
            get_execution_elements_result_paths(execution.algorithm_directory_paths)

        outlier_data_points: list[np.ndarray] = list([])

        # fill outlier_data_points with all information about which datapoint is an outlier
        # (1 bool array for each ExecutionElement result)
        for result_path in execution_result_path:
            outlier_data_points.append(eem_helper.compute_outlier_data_points(result_path))

        # Here starts the metric