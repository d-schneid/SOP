import math
from abc import ABC

import numpy as np
import pandas as pd

from MissingValuesRemover import MissingValuesRemover


class ThresholdMissingValuesRemover(MissingValuesRemover, ABC):
    """
    A cleaning_step for the dataset cleaning that rows that have to many missing values.
    """
    # threshold is a value between 0 and 1. It shows the proportion of
    # minimum None entries that a column that will be removed should have
    # Note: If threshold = 1 -> All data points are removed
    # Note: If threshold = 0 -> Only data points are removed, that have only missing values
    def __init__(self, threshold: float = 1):
        """
        :param threshold: Is a value in [0,1]. It shows the minimum percentual number/count of missing values that a row
        that will be removed will have. \n
            Note: If threshold = 1 -> All data points are removed \n
            Note: If threshold = 0 -> Only data points are removed, that have only missing values \n
        """
        self._threshold: float = max(0.0, min(1.0, threshold))  # clamp threshold to [0,1]

    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        """
        Removes rows that have more missing values than the threshold allows. \n
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        row_count: int = dataset_to_clean.shape[0]  # TODO: Check if 0 or 1 in array
        absolute_threshold: int = max(1, math.ceil(self._threshold * row_count))
        df = pd.DataFrame(dataset_to_clean)
        return df.dropna(thresh=absolute_threshold).to_numpy()
