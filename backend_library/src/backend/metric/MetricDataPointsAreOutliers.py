import numpy as np

from backend.DataIO import DataIO
from backend.metric.ExecutionElementMetricHelper import \
    ExecutionElementMetricHelper as eem_helper
from backend.metric.Metric import Metric
from pandas import DataFrame as df


class MetricDataPointsAreOutliers(Metric):

    def __init__(self, indices_mapping: list[int]):
        """
        :param indices_mapping: The first column of the metric result which shows the
        indices of the data points. \n
        Has to be the same size as each execution element result!
        (same amount of data points)
        """
        self._indices_mapping: list[int] = indices_mapping

    def compute_metric(self, metric_result_path: str,
                       algorithm_directory_paths: list[str]) -> None:
        """
        :param metric_result_path: The path where the metric will store its results to.
        Has to end with .csv
        :param algorithm_directory_paths: A list which contains all the paths to the
        folder of the selected algorithms.
        (Use the build in property algorithm_directory_paths in Execution)
        :return: None
        """
        assert metric_result_path.endswith(".csv")

        # Get all .csv files (ExecutionElement result)
        execution_result_path: list[str] = eem_helper. \
            get_execution_elements_result_paths(algorithm_directory_paths)

        # Fill outlier_data_points with all information
        # about which datapoint is an outlier
        # (1 bool array for each ExecutionElement result)
        outlier_data_points: list[np.ndarray] = list([])
        for result_path in execution_result_path:
            outlier_data_points. \
                append(eem_helper.compute_outlier_data_points(result_path))

        # Compute the metric result:
        data_points_outlier_in_subspace: list[int] = \
            eem_helper.compute_data_point_outlier_count(outlier_data_points)

        # convert into result
        assert len(self._indices_mapping) == len(data_points_outlier_in_subspace)
        metric_result: np.ndarray = df([self._indices_mapping,
                                        data_points_outlier_in_subspace]).\
            to_numpy()

        # save metric
        DataIO.save_write_csv(metric_result_path + ".running", metric_result_path,
                              np.asarray(metric_result).transpose(),
                              False)
