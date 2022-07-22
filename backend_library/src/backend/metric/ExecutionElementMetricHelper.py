from glob import glob
import os

import numpy as np
import pandas as pd

from backend.DataIO import DataIO
from backend.DataInfo import DataInfo


class ExecutionElementMetricHelper:
    @staticmethod
    def ComputeOutlierDataPoints(execution_element_result_path: str, quantile: float = 0.99) -> np.ndarray:
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

    #GetExecutionElementsResultPaths

    @staticmethod
    def GetCSVFilesInDirectory(execution_folder_path: str):
        """
        Return a list of all paths in this directory in its children directories that end with .csv
        :param execution_folder_path: The directory that should be scanned for files that end with .csv
        :return: The list of paths to .csv files.
        """
        all_csv_files: list[str] = [file
                                    for path, subdir, files in os.walk(execution_folder_path)
                                    for file in glob(os.path.join(path, "*.csv"))]
        return all_csv_files
