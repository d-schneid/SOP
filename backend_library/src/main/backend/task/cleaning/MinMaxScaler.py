from abc import ABC

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler as mms

from backend_library.src.main.backend.task.cleaning.FeatureScaler import FeatureScaler


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
        # check if dataset is empty
        if dataset_to_clean.shape[0] == 0 or dataset_to_clean.shape[1] == 0:
            raise ValueError("MinMaxScaler: input array is empty. Needs at least one row and one column")

        # check if column with only None-values exists
        for column_index in range(0, dataset_to_clean.shape[1]):
            column: np.ndarray = dataset_to_clean[:, column_index]
            if np.all((column == None)):
                raise ValueError("MinMaxScaler: None-column exists")

        scaler: mms = mms()
        scaler.fit(dataset_to_clean)
        transformed_dataset: np.ndarray = scaler.transform(dataset_to_clean)
        df = pd.DataFrame(transformed_dataset)
        return df.to_numpy()
