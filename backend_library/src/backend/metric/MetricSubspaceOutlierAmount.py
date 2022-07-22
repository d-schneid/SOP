from abc import ABC

import numpy as np

from backend.metric.Metric import Metric
from backend.task.execution.core.Execution import Execution
from backend.metric.ExecutionElementMetricHelper import ExecutionElementMetricHelper as eem_helper
from backend.DataIO import DataIO


class MetricSubspaceOutlierAmount(ABC, Metric):

    @staticmethod
    def compute_metric(execution: Execution, metric_result_path: str) -> None:
        """
        :param execution: The Execution to which this metric belongs to.
        :param metric_result_path: The path where the metric will store its results to. Has to end with .csv
        :return: None
        """
        assert metric_result_path.endswith(".csv")

        execution_result_paths: list[str] = eem_helper. \
            get_execution_elements_result_paths(execution.algorithm_directory_paths)

        outlier_data_points: list[np.ndarray] = list([])

        paths_divided_in_subspaces: dict = {}
        all_subspace_identifier: list[str] = \
            eem_helper.convert_paths_into_subspace_identifier(execution_result_paths)

        # Divide paths by their identifier
        for identifier in all_subspace_identifier:
            for path in execution_result_paths:
                if (paths_divided_in_subspaces.get(identifier)) is None:
                    paths_divided_in_subspaces[identifier] = list([path])
                else:
                    paths_divided_in_subspaces[identifier].append(path)




        #compute_data_point_outlier_count für jede subspace einzeln!!
        # split execution_result_path into the subspaces



        # Fill outlier_data_points with all information about which datapoint is an outlier
        # (1 bool array for each ExecutionElement result)
        for result_path in execution_result_path:
            outlier_data_points.append(eem_helper.compute_outlier_data_points(result_path))



        # Partition outlier_data_points into same subspace
        _subspace_amount: int = len(list(execution.subspaces))





        # Compute the metric result:







        subspace_outlier_amount: list[int] = eem_helper.compute_subspace_outlier_amount()

        # Create fist column of the array: The subspace identifier

        # save metric
        DataIO.save_write_csv(metric_result_path+".running", metric_result_path, TODO)