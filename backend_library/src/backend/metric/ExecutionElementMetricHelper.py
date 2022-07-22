from glob import glob
import os
from typing import Iterator

import numpy as np
import pandas as pd

from backend.DataIO import DataIO
from backend.DataInfo import DataInfo


class ExecutionElementMetricHelper:
    @staticmethod
    def compute_outlier_data_points(execution_element_result_path: str, quantile: float = 0.99) -> np.ndarray:
        """
        Interprets one result of an ExecutionElement and
        returns an array which says for each data point if it is an outlier or not \n
        :param execution_element_result_path: The execution element result whose outliers should be computed.
        The path has to end with .csv
        :param quantile: The used quantile to check if the data point is an outlier or not
        :return: An 1D bool array that says for each data point if it is an outlier or not
        """
        assert execution_element_result_path.endswith(".csv")
        assert os.path.isfile(execution_element_result_path)

        # The ExecutionElement result has to be in the right format: (first column indices, second outlier score)
        assert DataInfo.get_dataset_dimension(execution_element_result_path) == 2

        # Read ExecutionElement Result
        execution_element_result_df: pd.DataFrame = \
            pd.DataFrame(DataIO.read_cleaned_csv(execution_element_result_path))

        # Get quantile of second column (the outlier scores)
        min_outlier_score_to_be_an_outlier: float = execution_element_result_df.quantile(quantile).iloc[1]

        # Convert and return requested array
        # TODO: TEST THIS!!!
        outlier_data_points: list[bool] = list()

        for i in range(0, len(execution_element_result_df[1])):
            if float(execution_element_result_df[1][i]) >= min_outlier_score_to_be_an_outlier:
                outlier_data_points.append(True)
            else:
                outlier_data_points.append(False)

        return np.asarray(outlier_data_points)

    @staticmethod
    def get_execution_elements_result_paths(algorithm_directory_paths: list[str]):
        """ Gets all files that end with .csv in the selected directory. \n
        :param algorithm_directory_paths: The selected algorithm directories that should be scanned for the files.
        :return: A list containing all paths to the files that end with .csv in the inputted directories.
        """
        all_execution_element_results: list[str] = list([])
        for algorithm_directory in algorithm_directory_paths:
            assert os.path.isdir(algorithm_directory)

            all_execution_element_results.extend(ExecutionElementMetricHelper
                                                 .__get_csv_files_in_directory(algorithm_directory))
        return all_execution_element_results

    @staticmethod
    def __get_csv_files_in_directory(execution_folder_path: str) -> list[str]:
        """
        Return a list of all paths in this directory in its children directories that end with .csv. \n
        :param execution_folder_path: The directory that should be scanned for files that end with .csv.
        :return: The list of paths to .csv files.
        """
        all_csv_files: list[str] = [file
                                    for path, subdir, files in os.walk(execution_folder_path)
                                    for file in glob(os.path.join(path, "*.csv"))]
        return all_csv_files

    @staticmethod
    def compute_data_point_outlier_count(data_points_outlier_in_subspace: list[np.ndarray]) -> list[bool]:
        """
        :param data_points_outlier_in_subspace: The list containes for each subspace one entry.
        These entries are 1D bool array that say for each data point if it was an outlier or not
        :return: Return an list with an entry for each data point (ordered after the data point index).
        The entry shows the amount of subspaces in which this data point was detected as an outlier
        """
        assert len(data_points_outlier_in_subspace) > 0
        assert data_points_outlier_in_subspace[0].shape[0] == 1

        data_points_outlier_count: list[int] = [0] * data_points_outlier_in_subspace[0].shape[0]

        for subspace_result in data_points_outlier_in_subspace:
            for data_point in range(0, subspace_result.shape[0]):
                if subspace_result[data_point] is True:
                    data_points_outlier_count[data_point] += 1

        return data_points_outlier_count

