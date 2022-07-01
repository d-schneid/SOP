import math
from abc import ABC

import numpy as np
import pandas as pd

from MissingValuesRemover import MissingValuesRemover


class ThresholdMissingValuesRemover(MissingValuesRemover, ABC):
    # threshold is a value between 0 and 1. It shows the proportion of
    # minimum None entries that a column that will be removed should have
    # Note: If threshold = 1 -> All data points are removed
    # Note: If threshold = 0 -> Only data points are removed, that have only missing values
    def __init__(self, threshold: float = 1):
        self._threshold: float = max(0.0, min(1.0, threshold))  # clamp threshold to [0,1]

    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        row_count: int = dataset_to_clean.shape[0]  # TODO: Check if 0 or 1 in array
        absolute_threshold: int = max(1, math.ceil(self._threshold * row_count))
        df = pd.DataFrame(dataset_to_clean)
        return df.dropna(thresh=absolute_threshold).to_numpy()
