import math
from abc import ABC

import numpy as np
import pandas as pd

from backend.task.cleaning.MissingValuesRemover import MissingValuesRemover
from backend.task.cleaning.DatasetCleaningStepExceptionHanding \
    import DatasetCleaningStepExceptionHandling as eh


class RowOrColumnMissingValuesRemover(MissingValuesRemover, ABC):
    """
    A cleaning_step for the dataset cleaning that removes rows/columns that have only missing values.
    """

    def __init__(self, axis: int = 0):
        """
        :param axis:
            # 0 -> remove rows
            # 1 -> remove columns
        """

        if axis != 0 and axis != 1:  # Allow only axis = 0 or = 1
            raise ValueError("ThresholdMissingValuesRemover" + ": only axis = 0 or 1 allowed.")
        self._axis: int = axis

    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        """
        Removes rows/columns that have only missing values. \n
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        # exception logic
        eh.check_non_empty_array(dataset_to_clean, "ThresholdMissingValuesRemover")

        # ThresholdMissingValuesRemover logic
        # normal case (more than one row)
        if len(dataset_to_clean.shape) > 1:
            df: pd.DataFrame = pd.DataFrame(dataset_to_clean)
            cleaned_array: np.ndarray = df.dropna(axis=self._axis, how='all').to_numpy()
            return cleaned_array

        # edge case handling: one row only
        else:
            if self._axis == 1:  # remove column (one entry)
                columns_to_drop = []
                for idx in range(0, dataset_to_clean.shape[0]):
                    if str(type(dataset_to_clean[idx])) == '<class \'NoneType\'>':  # TODO unschön, vllt schöner machen
                        columns_to_drop.append(idx)
                return np.asarray(np.delete(dataset_to_clean, columns_to_drop, axis=0))
            else:  # remove row
                for idx in range(0, dataset_to_clean.shape[0]):
                    if str(type(dataset_to_clean[idx])) != '<class \'NoneType\'>':  # TODO unschön, vllt schöner machen
                        return dataset_to_clean  # no none row -> don't do anything
                    return np.zeros((0, 0))  # empty dataset
