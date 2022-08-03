import os
import shutil
from typing import Optional

import numpy as np
import pandas as pd

from backend.AnnotatedDataset import AnnotatedDataset


class DataIO:
    @staticmethod
    def read_annotated(path: str, is_cleaned: bool, has_header: bool = True,
                       has_row_numbers: bool = True) -> AnnotatedDataset:
        """
        Reads an annotated Dataset from a file
        :param path: the path where the dataset is
        :param is_cleaned: whether the data-section consists of floats only
        :param has_header: whether the file has headers (false will generate new ones)
        :param has_row_numbers: whether the file has row numbers
        (false will generate them)
        :return: an annotated dataset from the file
        """
        base = pd.read_csv(path, dtype=object).to_numpy()
        anno_ds = AnnotatedDataset(base, None, None,
                                   not has_header, not has_row_numbers)
        if is_cleaned:
            anno_ds.data = anno_ds.data.astype(np.float32)
        else:
            anno_ds.data = DataIO.__save_convert_to_float(anno_ds.data)
        return anno_ds

    @staticmethod
    def read_cleaned_csv(path: str, has_header: Optional[int] = None) -> np.ndarray:
        """
        Returns the cleaned dataset. \n
        Raises an ValueError exception if the dataset is not cleaned (cast into float32 did not succeed).
        :param path: The absolute path where to read the dataset from.
        :param has_header: The header of the dataset that should be read.
        :return: The cleaned dataset (or an exception).
        """
        assert os.path.isfile(path)

        loaded_dataset = DataIO.read_uncleaned_csv(path, has_header)
        cleaned_dataset: np.ndarray = loaded_dataset.astype(np.float32)  # cast ndarray to float32

        return cleaned_dataset

    @staticmethod
    def read_uncleaned_csv(path: str, has_header: Optional[int] = 0) -> np.ndarray:
        """
        Returns the uncleaned dataset. \n
        :param path: The absolute path where to read the dataset from.
        :param has_header: The header of the dataset that should be read.
        :return: The uncleaned dataset.
        """
        assert os.path.isfile(path)

        df: pd.DataFrame = pd.read_csv(path, dtype=object, header=has_header)
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
    def write_csv(path: str, data: np.ndarray, add_index_column: bool = False,
                  has_header: bool = False):
        """
        Writes the given 2D-dataset to a csv-file.

        :param path: The absolute path to the location of the csv-file
                        to be created and written to.
                     If this file is already existing, it is overridden.
        :param data: The dataset that should be written to the file.
        :param add_index_column: If True create an additional column
            at the start of the array with
        indexes for each row. If False don't change anything.
        :param has_header: Has the dataset that should be written a header?
        """

        df = pd.DataFrame(data)
        assert len(df.shape) == 2

        df.to_csv(path, index=add_index_column, header=has_header)

    @staticmethod
    def save_write_csv(running_path: str, final_path: str, data: np.ndarray,
                       add_index_column: bool = False, has_header: bool = False):
        """
        Writes the given 2D-dataset to a csv-file.
        Unlike write_csv although, it does this in a way so that corrupted files, e.g. due to
        server crashes, can be recognized.

        This works the following way:
        While the data is written to the file, it is saved to the path_running path and after
        the writing has finished is moved to the path_cleaning path.
        For this to work, both paths have to be on the same file system.

        :param running_path: The path the csv-data is saved in during the writing process.
                             Should be on the same file system as path_final.
                             If this file is already existing, it is overridden (= deleted).
        :param final_path: The path the csv-file is saved in after the writing has finished.
                           Should be on the same file system as path_running.
                           If this file is already existing, it is overridden.
        :param data: The dataset that should be written to the file.
        :param add_index_column: If True create an additional column at the start of the array with
                                 indexes for each row. If False don't change anything.
        :param has_header: Has the dataset that should be written a header?
        """
        DataIO.write_csv(running_path, data, add_index_column, has_header)
        shutil.move(running_path, final_path)
