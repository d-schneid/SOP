from abc import ABC

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler as mms

from backend.AnnotatedDataset import AnnotatedDataset
from backend.task.cleaning.FeatureScaler import FeatureScaler
from backend.task.cleaning.DatasetCleaningStepExceptionHanding \
    import DatasetCleaningStepExceptionHandling as eh


class MinMaxScaler(FeatureScaler, ABC):
    """
    A cleaning_step for the dataset cleaning that uses
    MinMaxScaling to normalise the dataset.
    """

    def do_cleaning(self, dataset_to_clean: AnnotatedDataset) -> AnnotatedDataset:
        """
        Uses MinMaxScaling to normalise the dataset. \n
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        # exception handling
        assert len(dataset_to_clean.data.shape) == 2
        eh.check_non_none_column(dataset_to_clean.data, "MinMaxScaler")

        # MinMaxScaling logic
        scaler: mms = mms()
        scaler.fit(dataset_to_clean.data)

        transformed_dataset: np.ndarray = scaler.transform(dataset_to_clean.data)
        df = pd.DataFrame(transformed_dataset)

        dataset_to_clean.data = df.to_numpy()
        return dataset_to_clean
