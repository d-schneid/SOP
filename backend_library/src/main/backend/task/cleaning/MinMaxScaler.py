from abc import ABC

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler as mms

from backend_library.src.main.backend.task.cleaning.FeatureScaler import FeatureScaler
from backend_library.src.main.backend.task.cleaning.DatasetCleaningStepExceptionHanding \
    import DatasetCleaningStepExceptionHandling as eh


class MinMaxScaler(FeatureScaler, ABC):
    """
    A cleaning_step for the dataset cleaning that uses MinMaxScaling to normalise the dataset.
    """

    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        """
        Uses MinMaxScaling to normalise the dataset. \n
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        # exception handling
        eh.check_non_empty_array(dataset_to_clean, "MinMaxScaler")
        eh.check_non_none_column(dataset_to_clean, "MinMaxScaler")

        # MinMaxScaling logic
        scaler: mms = mms()
        scaler.fit(dataset_to_clean)
        transformed_dataset: np.ndarray = scaler.transform(dataset_to_clean)
        df = pd.DataFrame(transformed_dataset)
        return df.to_numpy()
