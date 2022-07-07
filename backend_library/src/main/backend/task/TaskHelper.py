import csv
import os

import numpy as np
from collections.abc import Iterable


class TaskHelper:
    """
    Static helping methods for the subclasses of Task.
    """
    @staticmethod
    def save_error_csv(path: str, error_message: str) -> None:
        """ Converts path into the error_file_path and saves the error-csv-file there.
        :param path: The absolute path where the csv will be stored (contains the name of the csv and ends with .csv).
        :param error_message: The error message that will be written into the error_csv file.
        :return: None
        """
        error_file_path: str = TaskHelper.convert_to_error_csv_path(path)
        error_message: str = error_message
        with open(error_file_path, 'w') as error_csv:
            writer = csv.writer(error_csv)
            writer.writerow(error_message)

    @staticmethod
    def convert_to_error_csv_path(path: str) -> str:
        """ Converts the path to the path where the error_csv will be stored.
        :param path: The absolute path that will be converted.
        :return: The converted path into the error_csv path.
        """
        return path + ".error"

    @staticmethod
    def is_float_csv(csv_to_check: np.ndarray) -> bool:
        """ Checks if the array only contains float_32.
        The parsing of the values into float_32 has to be done before calling this method.
        :param csv_to_check: The array that should be checked.
        :return: True if only float_32
        """
        dtype: np.dtype = csv_to_check.dtype
        if dtype == np.float32:
            return True
        return False

    @staticmethod
    def create_directory(path: str) -> None:
        """
        :param path: The absolute path where the new directory will be created
        :return: None
        """
        if not os.path.isdir(path):
            new_directory = os.path.join(path)  # TODO: Test this
            os.mkdir(new_directory)

    @staticmethod
    def iterable_length(iterable: Iterable) -> int:
        """
        :param iterable: The iterable whose length is requested
        :return: Returns the length of the iterable.
        """
        return sum(1 for e in iterable)
