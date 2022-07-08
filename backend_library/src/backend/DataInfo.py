import os

import numpy as np
import pandas as pd


class DataInfo:
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
