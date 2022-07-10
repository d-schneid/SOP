import os

import numpy as np
import pandas as pd


class DataIO:
    @staticmethod
    def read_cleaned_csv(path: str) -> np.ndarray:
        """
        Returns the cleaned dataset. \n
        Raises an ValueError exception if the dataset is not cleaned (cast into float32 did not succeed).
        :param path: The absolute path where to read the dataset from.
        :return: The cleaned dataset (or an exception).
        """
        loaded_dataset = DataIO.read_uncleaned_csv(path)
        cleaned_dataset: np.ndarray = loaded_dataset.astype(
                np.float32)  # cast ndarray to float32

        return cleaned_dataset

    @staticmethod
    def read_uncleaned_csv(path: str) -> np.ndarray:
        """
        Returns the uncleaned dataset. \n
        :path: The absolute path where to read the dataset from.
        :return: The uncleaned dataset.
        """
        assert os.path.isfile(path) is True

        df: pd.DataFrame = pd.read_csv(path, dtype=object)
        return df.to_numpy()

    @staticmethod
    def write_csv(path: str, data: np.ndarray, add_index_column: bool = False):
        """
        Writes the given dataset to a csv-file.
        :param path: The absolute path to the location of the csv-file to be created and written to.
        :param data: The dataset that should be created and written to.
        :param add_index_column: If True create an additional column at the start of the array with
        indexes for each row. If False don't change anything.
        :data: The dataset to write to the file.
        """

        df = pd.DataFrame(data)
        df.to_csv(path, index=add_index_column)
