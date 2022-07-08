from abc import ABC

import numpy as np
import pandas as pd

from backend.task.cleaning.Imputation import Imputation
from backend.task.cleaning.DatasetCleaningStepExceptionHanding \
    import DatasetCleaningStepExceptionHandling as eh


class ImputationMode(Imputation, ABC):
    """
    A cleaning_step for the dataset cleaning that removes missing values through the mode of the column.
    """

    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        """
        Exchanges missing values through the mode. \n
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """

        # exception handling
        eh.check_non_none_column(dataset_to_clean, "ImputationMode")

        # Mode logic
        df = pd.DataFrame(dataset_to_clean)
        for column in df:
            df[column] = df[column].fillna(df[column].mean)
        return df.to_numpy()
