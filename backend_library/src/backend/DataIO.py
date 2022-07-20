import os
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
        assert os.path.isfile(path)

        loaded_dataset = DataIO.read_uncleaned_csv(path)
        cleaned_dataset: np.ndarray = loaded_dataset.astype(np.float32)  # cast ndarray to float32

        return cleaned_dataset

    @staticmethod
    def read_uncleaned_csv(path: str) -> np.ndarray:
        """
        Returns the uncleaned dataset. \n
        :path: The absolute path where to read the dataset from.
        :return: The uncleaned dataset.
        """
        assert os.path.isfile(path)

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
                        continue  # leave value the same if it can't be cast
        else:  # edge case: only one row
            for n in range(0, to_convert.shape[0]):
                try:
                    to_convert[n] = float(to_convert[n])
                except ValueError:
                    continue  # leave value the same if it can't be cast
        return to_convert

    @staticmethod
    def write_csv(path: str, data: np.ndarray, add_index_column: bool = False):
        """
        Writes the given 2D-dataset to a csv-file.

        :param path: The absolute path to the location of the csv-file to be created and written to.
                     If this file is already existing, it is overridden.
        :param data: The dataset that should be written to the file.
        :param add_index_column: If True create an additional column at the start of the array with
        indexes for each row. If False don't change anything.
        """

        # delete file if already existing
        if os.path.isfile(path):
            os.remove(path)

        df = pd.DataFrame(data)
        assert len(df.shape) == 2

        df.to_csv(path, index=add_index_column)

    @staticmethod
    def save_write_csv(path_running: str, path_final: str, data: np.ndarray, add_index_column: bool = False):
        """
        Writes the given 2D-dataset to a csv-file.
        Unlike write_csv although, it does this in a way so that corrupted files, e.g. due to
        server crashes, can be recognized.

        This works the following way:
        While the data is written to the file, it is saved to the path_running path and after
        the writing has finished is moved to the path_cleaning path.
        For this to work, both paths have to be on the same file system.

        :param path_running: The path the csv-data is saved in during the writing process.
                             Should be on the same file system as path_final.
                             If this file is already existing, it is overridden (= deleted).
        :param path_final: The path the csv-file is saved in after the writing has finished.
                           Should be on the same file system as path_running.
                           If this file is already existing, it is overridden.
        :param data: The dataset that should be written to the file.
        :param add_index_column: If True create an additional column at the start of the array with
                                 indexes for each row. If False don't change anything.
        """

        # delete final_path file if already existing
        if os.path.isfile(path_final):
            os.remove(path_final)

        DataIO.write_csv(path_running, data, add_index_column)

        # is an atomic operation, *if* both paths are on the same file system
        shutil.move(path_running, path_final)


