from abc import ABC

import numpy as np
import pandas as pd

from backend.AnnotatedDataset import AnnotatedDataset
from backend.task.cleaning.CategoricalDataHandler import CategoricalDataHandler
from backend.task.cleaning.DatasetCleaningStepExceptionHanding \
    import DatasetCleaningStepExceptionHandling as eh


class CategoricalColumnRemover(CategoricalDataHandler, ABC):
    """
    A cleaning_step for the dataset cleaning that removes
    all columns that contain categorical data.
    """

    def do_cleaning(self, dataset_to_clean: AnnotatedDataset) -> AnnotatedDataset:
        """
        Remove all columns that contain categorical data. \n
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        # exception logic
        assert len(dataset_to_clean.data.shape) == 2
        eh.check_no_empty_array(dataset_to_clean.data, "CategoricalColumnRemover")

        # CategoricalColumnRemover logic
        df = pd.DataFrame(dataset_to_clean.to_single_array())
        columns_to_drop = []

        # start with the second column because the first column are the indices
        for column in range(1, df.columns.size):
            column_df: pd.DataFrame = pd.DataFrame(df[column])

            # header are always strings -> remove them
            column_df = column_df.iloc[1:, :]

            # check if any entry of the column is a string
            if column_df.applymap(type).eq(str).any().any():
                columns_to_drop.append(column)
                continue

        cleaned_single_array_dataset: np.ndarray = \
            df.drop(df.columns[columns_to_drop], axis=1).to_numpy()

        return AnnotatedDataset(cleaned_single_array_dataset)
