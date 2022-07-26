import pandas as pd
from backend.DataIO import DataIO
from typing import Optional, Tuple


class DatasetHelper:

    @staticmethod
    def is_dataset_valid(path: str) -> bool:
        """
        Checks, whether the dataset saved at the given path is valid.
        :param path: The path where the dataset to check is saved at.
        :return: True, if the dataset is valid; otherwise False
        """
        try:
            has_header: Optional[int] = 0
            DataIO.read_uncleaned_csv(path, has_header=has_header)

            # if no error was thrown, the dataset is valid
            return True

        except DataIO.DataIoInputException:
            # if an error was thrown, the dataset is invalid
            return False

    @staticmethod
    def shape(path: str) -> Tuple[int, int]:
        """
        Determines the shape of the given dataset.
        :param path: The path to the dataset.
        :return: The shape of dataset, as a tuple, whereby the first component describes the number of lines
        and the second component describes the number of rows.
        """
        return pd.read_csv(path).shape

    @staticmethod
    def number_datapoints(path: str) -> int:
        """
        Determines the number of datapoints in a given dataset.
        :param path: The path to the dataset.
        :return: The number of datapoints of the given dataset.
        """
        return DatasetHelper.shape(path)[0]

    @staticmethod
    def number_dimensions(path: str) -> int:
        """
        Determines the number of dimensions of a given datapoint.
        :param path: The path to the dataset.
        :return: The number of dimensions of the given dataset.
        """
        return DatasetHelper.shape(path)[1]