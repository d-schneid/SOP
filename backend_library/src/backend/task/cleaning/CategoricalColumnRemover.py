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
        eh.check_non_empty_array(dataset_to_clean.data, "CategoricalColumnRemover")

        # CategoricalColumnRemover logic
        df = pd.DataFrame(dataset_to_clean.to_single_array())
        columns_to_drop = []

        # normal case -> more than one row
        if len(dataset_to_clean.data.shape) > 1:
            for column in df:
                column_df: pd.DataFrame = pd.DataFrame(df[column])
                if column_df.applymap(type).eq(str).any().any():
                    columns_to_drop.append(column)
                    continue
            cleaned_single_array_dataset: np.ndarray = \
                df.drop(df.columns[columns_to_drop], axis=1).to_numpy()

            return AnnotatedDataset(cleaned_single_array_dataset)

        # only one row -> needs special treatment
        else:
            for idx in range(0, dataset_to_clean.data.shape[0]):
                if type(dataset_to_clean.data[idx]) is str:
                    columns_to_drop.append(idx)

            dataset_to_clean.headers = \
                np.asarray(np.delete(dataset_to_clean.headers, columns_to_drop, axis=0))
            dataset_to_clean.data = \
                np.asarray(np.delete(dataset_to_clean.data, columns_to_drop, axis=0))

            return dataset_to_clean
