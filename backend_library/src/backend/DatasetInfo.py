import os
from typing import Optional

import pandas as pd

from backend.DataIO import DataIO


class DatasetInfo:
    @staticmethod
    def get_dataset_dimension(dataset_path) -> int:
        """
        Return the dimension (number of columns) of a dataset.
        :param dataset_path: The dataset that will be inspected.
        :return: The dimension of the Dataset
        """
        assert os.path.isfile(dataset_path)

        try:
            df_first_row = pd.read_csv(dataset_path, nrows=1)
        except pd.errors.EmptyDataError:
            return 0

        return df_first_row.shape[1]

    @staticmethod
    def get_dataset_datapoint_amount(dataset_path) -> int:
        """
        Return the amount of data points in the dataset.
        :param dataset_path: The dataset that will be inspected.
        :return: The amount of data points int the Dataset
        """
        assert os.path.isfile(dataset_path)

        try:
            df_first_column = pd.read_csv(dataset_path, usecols=[0])
        except pd.errors.EmptyDataError:
            return 0

        return df_first_column.shape[0]

    @staticmethod
    def is_dataset_valid(path: str) -> bool:
        """
        Checks, whether the dataset saved at the given path is valid.
        :param path: The path where the dataset to check is saved at.
        :return: True, if the dataset is valid; otherwise False
        """

        assert os.path.isfile(path)

        try:
            has_header: Optional[int] = 0
            DataIO.read_uncleaned_csv(path, has_header=has_header)

            # if no error was thrown upon reading, the dataset is valid
            return True

        except DataIO.DataIoInputException:
            # if an error was thrown upon reading the dataset is invalid
            return False
