from abc import ABC

import numpy as np
import pandas as pd

from backend.task.cleaning.CategoricalDataHandler import CategoricalDataHandler
from backend.task.cleaning.DatasetCleaningStepExceptionHanding \
    import DatasetCleaningStepExceptionHandling as eh


class CategoricalColumnRemover(CategoricalDataHandler, ABC):
    """
    A cleaning_step for the dataset cleaning that removes all columns that contain categorical data.
    """

    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        """
        Remove all columns that contain categorical data. \n
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        # exception logic
        eh.check_non_empty_array(dataset_to_clean, "CategoricalColumnRemover")

        # CategoricalColumnRemover logic
        df = pd.DataFrame(dataset_to_clean)
        columns_to_drop = []
        for column in df:
            column_df: pd.DataFrame = pd.DataFrame(df[column])
            if column_df.applymap(type).eq(str).any().any():
                columns_to_drop.append(column)
                continue

        return df.drop(df.columns[columns_to_drop], axis=1).to_numpy()
