import math
from abc import ABC

import numpy as np
import pandas as pd

from backend.AnnotatedDataset import AnnotatedDataset
from backend.task.cleaning.MissingValuesRemover import MissingValuesRemover
from backend.task.cleaning.DatasetCleaningStepExceptionHanding \
    import DatasetCleaningStepExceptionHandling as eh


class RowOrColumnMissingValuesRemover(MissingValuesRemover, ABC):
    """
    A cleaning_step for the dataset cleaning that removes rows/columns
    that have only missing values.
    """

    def __init__(self, axis: int = 0):
        """
        :param axis:
            # 0 -> remove rows
            # 1 -> remove columns
        """

        if axis != 0 and axis != 1:  # Allow only axis = 0 or = 1
            raise ValueError("ThresholdMissingValuesRemover" +
                             ": only axis = 0 or 1 allowed.")
        self._axis: int = axis

    def do_cleaning(self, dataset_to_clean: AnnotatedDataset) -> AnnotatedDataset:
        """
        Removes rows/columns that have only missing values. \n
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        # exception logic
        eh.check_non_empty_array(dataset_to_clean.data, "ThresholdMissingValuesRemover")

        # ThresholdMissingValuesRemover logic
        # normal case (more than one row)
        if len(dataset_to_clean.data.shape) > 1:
            df: pd.DataFrame = pd.DataFrame(dataset_to_clean.to_single_array())

            df.dropna(axis=self._axis, how='any', tresh=1, inplace=True)

            return AnnotatedDataset(df.to_numpy())

        # edge case handling: one row only
        else:
            if self._axis == 1:  # remove column (one entry)
                columns_to_drop = []
                for idx in range(0, dataset_to_clean.data.shape[0]):
                    if str(type(dataset_to_clean.data[idx])) \
                            == '<class \'NoneType\'>':  # check if None-value
                        columns_to_drop.append(idx)

                # remove the None-columns (in the headers AND data):
                dataset_to_clean.headers = \
                    np.asarray(np.delete(dataset_to_clean.headers,
                                         columns_to_drop, axis=0))
                dataset_to_clean.data = \
                    np.asarray(np.delete(dataset_to_clean.data,
                                         columns_to_drop, axis=0))
                return dataset_to_clean
            else:  # remove row
                for idx in range(0, dataset_to_clean.data.shape[0]):
                    if str(type(dataset_to_clean.data[idx])) \
                            != '<class \'NoneType\'>':  # check if not None-value
                        return dataset_to_clean  # no none row -> don't do anything
                    dataset_to_clean.data = np.zeros((0, 0))  # empty dataset
                    return dataset_to_clean
