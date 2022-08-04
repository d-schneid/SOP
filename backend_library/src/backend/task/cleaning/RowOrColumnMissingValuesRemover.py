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
        assert len(dataset_to_clean.data.shape) == 2
        eh.check_non_empty_array(dataset_to_clean.data, "ThresholdMissingValuesRemover")

        # ThresholdMissingValuesRemover logic
        df: pd.DataFrame = pd.DataFrame(dataset_to_clean.to_single_array())

        df = df.dropna(axis=self._axis, how='any', thresh=2)

        return AnnotatedDataset(df.to_numpy())
