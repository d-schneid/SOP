import shutil

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

        df: pd.DataFrame = pd.read_csv(path, dtype=object)
        return DataIO.__save_convert_to_float(df.to_numpy())

    @staticmethod
    def __save_convert_to_float(to_convert: np.ndarray) -> np.ndarray:
        """
        Converts all values to float that can be converted. Leaves the other values as they are. \n
        :param to_convert: The array that should be converted.
        :return: The converted array.
        """
        assert len(to_convert.shape) > 0

        if len(to_convert.shape) > 1:
            for n in range(0, to_convert.shape[0]):
                for m in range(0, to_convert.shape[1]):
                    try:
                        to_convert[n, m] = float(to_convert[n, m])
                    except ValueError:
                        continue  # leave value the same if it can't be casted
        else:  # edge case: only one row
            for n in range(0, to_convert.shape[0]):
                try:
                    to_convert[n] = float(to_convert[n])
                except ValueError:
                    continue  # leave value the same if it can't be casted
        return to_convert

    @staticmethod
    def write_csv(path: str, data: np.ndarray, add_index_column: bool = False):
        """
        Writes the given dataset to a csv-file. \n
        :param path: The absolute path to the location of the csv-file to be created and written to.
        :param data: The dataset that should be created and written to.
        :param add_index_column: If True create an additional column at the start of the array with
        indexes for each row. If False don't change anything.
        :data: The dataset to write to the file.
        """

        df = pd.DataFrame(data)
        df.to_csv(path, index=add_index_column)

    @staticmethod
    def save_write_csv(running_path: str, final_path: str, data: np.ndarray, add_index_column: bool = False):
        """
        Write csv first at running path (e.g. ends with .running) and renames the file after writing
        it to the final path.
        :param running_path: The absolute path where to write the csv file to before renaming it.
        :param final_path: The absolute path where the final written csv file will be stored.
        :param data: The dataset that should be created and written to.
        :param add_index_column: If True create an additional column at the start of the array with
        indexes for each row. If False don't change anything.
        :return:
        """
        DataIO.write_csv(running_path, data, add_index_column)
        shutil.move(running_path, final_path)
