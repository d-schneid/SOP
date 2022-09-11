import csv
import os

import pandas as pd


class DatasetInfo:
    @staticmethod
    def get_dataset_dimension(dataset_path: str, has_row_mapping: bool = True) -> int:
        """
        Return the dimension (number of columns) of a dataset.
        :param dataset_path: The dataset that will be inspected.
        :param has_row_mapping: Does the dataset has an extra column with the indices
        of the data points?
        :return: The dimension of the Dataset
        """
        assert os.path.isfile(dataset_path)

        try:
            df_first_row = pd.read_csv(dataset_path, nrows=1)

        except pd.errors.EmptyDataError:
            return 0

        dataset_dimension: int = df_first_row.shape[1]

        # 1 dim less when the dataset has row_mapping
        if has_row_mapping:
            dataset_dimension = max(0, dataset_dimension - 1)

        return dataset_dimension

    @staticmethod
    def get_dataset_datapoint_amount(dataset_path: str, has_header: bool = True) -> int:
        """
        Return the amount of data points in the dataset.
        :param dataset_path: The dataset that will be inspected.
        :param has_header: Does the dataset has an extra row with headers?
        :return: The amount of data points int the Dataset
        """
        assert os.path.isfile(dataset_path)

        try:
            df_first_column = pd.read_csv(dataset_path, usecols=[0], header=None)
        except pd.errors.EmptyDataError:
            return 0

        datapoint_amount: int = df_first_column.shape[0]
        if has_header:
            datapoint_amount = max(0, datapoint_amount - 1)

        return datapoint_amount

    @staticmethod
    def is_dataset_valid(path: str) -> bool:
        """
        Checks, whether the dataset saved at the given path is valid.
        :param path: The path where the dataset to check is saved at.
        :return: True, if the dataset is valid; otherwise False
        """

        assert os.path.isfile(path)

        try:
            with open(path, newline="") as file:
                csv_reader = csv.reader(file, dialect=DatasetInfo.RfcCsvDialect)

                col_num = None

                for row in csv_reader:
                    if col_num is None:
                        col_num = len(row)
                    elif col_num != len(row):
                        return False

                # if all rows have the same amount of columns, return True
                return True

        except (csv.Error, UnicodeDecodeError):
            return False

    class RfcCsvDialect(csv.Dialect):
        delimiter = ","
        doublequote = True
        escapechar = None
        lineterminator = "\n\r"  # <-- not important for reading
        quotechar = '"'
        quoting = csv.QUOTE_MINIMAL
        skipinitialspace = False
        strict = True
