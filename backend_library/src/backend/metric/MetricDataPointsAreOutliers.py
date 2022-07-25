import numpy as np

from backend.DataIO import DataIO
from backend.metric.ExecutionElementMetricHelper import ExecutionElementMetricHelper as eem_helper
from backend.metric.Metric import Metric


class MetricDataPointsAreOutliers(Metric):

    @staticmethod
    def compute_metric(metric_result_path: str, algorithm_directory_paths: list[str]) -> None:
        """
        :param metric_result_path: The path where the metric will store its results to. Has to end with .csv
        :param algorithm_directory_paths: A list which contains all the paths to the folder of the selected algorithms.
        (Use the build in property algorithm_directory_paths in Execution)
        :return: None
        """
        assert metric_result_path.endswith(".csv")

        # Get all .csv files (ExecutionElement result)
        execution_result_path: list[str] = eem_helper. \
            get_execution_elements_result_paths(algorithm_directory_paths)

        # Fill outlier_data_points with all information about which datapoint is an outlier
        # (1 bool array for each ExecutionElement result)
        outlier_data_points: list[np.ndarray] = list([])
        for result_path in execution_result_path:
            outlier_data_points.append(eem_helper.compute_outlier_data_points(result_path))

        # Compute the metric result:
        data_points_outlier_in_subspace: list[int] = eem_helper.compute_data_point_outlier_count(outlier_data_points)

        # save metric
        DataIO.save_write_csv(metric_result_path + ".running", metric_result_path,
                              np.asarray([data_points_outlier_in_subspace]), True)
