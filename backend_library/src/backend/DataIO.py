import os

import numpy as np
import numpy.typing as npt
import pandas as pd


class DataIO:
    @staticmethod
    def read_cleaned_csv(path: str) -> np.ndarray:
        """
        Returns the cleaned dataset. \n
        Raises an ValueError exception if the dataset is not cleaned (cast into float32 did not succeed).
        :param path: The absolute path were to read the dataset from.
        :return: The cleaned Dataset (Or an exception).
        """
        loaded_dataset = DataIO.read_uncleaned_csv(path)
        cleaned_dataset: np.ndarray = loaded_dataset.astype(
                np.float32)  # cast ndarray to float32

        return cleaned_dataset

    @staticmethod
    def read_uncleaned_csv(path: str) -> np.ndarray:
        """
        Returns the uncleaned dataset. \n
        :param path: The absolute path were to read the dataset from.
        :return: The uncleaned dataset.
        """
        assert os.path.isfile(path) is True

        df: pd.DataFrame = pd.read_csv(path)
        return df.to_numpy()

    @staticmethod
    def write_csv(path: str, data: np.ndarray):
        # TODO: Finn
        pass
