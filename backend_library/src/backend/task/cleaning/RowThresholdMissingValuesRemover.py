import math
from abc import ABC

import numpy as np
import pandas as pd

from backend.task.cleaning.MissingValuesRemover import MissingValuesRemover


class ThresholdMissingValuesRemover(MissingValuesRemover, ABC):
    """
    A cleaning_step for the dataset cleaning that rows that have to many missing values.
    """
    def __init__(self, threshold: float = 1):
        """
        :param threshold: Is a value in [0,1]. It shows the relative number of values a row should have
        that are not equal to None. If it has fewer values != None the row gets deleted. \n
            # 0 -> no data points will be removed (no None needed for a row to survive)
            # 1 -> Only data points without None will survive
        """
        self._threshold: float = max(0.0, min(1.0, threshold))  # clamp threshold to [0,1]

    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        """
        Removes rows that have more missing values than the threshold allows. \n
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        column_count: int = dataset_to_clean.shape[1]
        absolute_threshold: int = max(0, math.ceil(self._threshold * column_count))
        df: pd.DataFrame = pd.DataFrame(dataset_to_clean)
        return df.dropna(how='any', thresh=absolute_threshold).to_numpy()

