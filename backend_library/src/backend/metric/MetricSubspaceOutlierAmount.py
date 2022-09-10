from pathlib import Path

import numpy as np

from backend.DataIO import DataIO
from backend.metric.ExecutionElementMetricHelper import \
    ExecutionElementMetricHelper as eem_helper
from backend.metric.Metric import Metric
from pandas import DataFrame as df

from backend.task.TaskHelper import TaskHelper


class MetricSubspaceOutlierAmount(Metric):

    @staticmethod
    def compute_metric(metric_result_path: str,
                       algorithm_directory_paths: list[str]) -> None:
        """
        :param metric_result_path: The path where the metric will store its results to.
        Has to end with .csv
        :param algorithm_directory_paths: A list which contains all the paths
        to the folder of the selected algorithms.
        (Use the build in property algorithm_directory_paths in Execution)
        :return: None
        """
        assert metric_result_path.endswith(".csv")

        # Get all .csv files (ExecutionElement result)
        execution_result_paths: list[str] = eem_helper. \
            get_execution_elements_result_paths(algorithm_directory_paths)

        # Get subspace identifier
        outlier_data_points_divided_in_subspaces: dict = {}
        all_subspace_identifier: list[str] = \
            eem_helper.convert_paths_into_subspace_identifier(execution_result_paths)

        # create Error file and stop computation if no result file exists
        if len(all_subspace_identifier) == 0:
            error_path: str = TaskHelper.convert_to_error_csv_path(metric_result_path)
            eem_helper.write_empty_execution_error_message(error_path)
            return

        # Divide outlier_data_points by their subspace identifier
        for identifier in all_subspace_identifier:
            for path in execution_result_paths:
                if Path(path).stem != identifier:
                    continue

                if (outlier_data_points_divided_in_subspaces.get(identifier)) is None:
                    outlier_data_points_divided_in_subspaces[identifier] \
                        = list([eem_helper.compute_outlier_data_points(path)])
                else:
                    outlier_data_points_divided_in_subspaces[identifier] \
                        .append(eem_helper.compute_outlier_data_points(path))

        # compute metric
        outlier_data_points: list[int] = eem_helper.compute_subspace_outlier_amount(
            outlier_data_points_divided_in_subspaces)

        # convert into result
        metric_result: np.ndarray = df(
            [all_subspace_identifier, outlier_data_points]).to_numpy().transpose()

        # save metric result
        DataIO.save_write_csv(metric_result_path + ".running", metric_result_path,
                              metric_result, False)
