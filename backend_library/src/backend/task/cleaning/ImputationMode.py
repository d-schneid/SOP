from abc import ABC

import numpy as np
import pandas as pd
from scipy import stats

from backend.AnnotatedDataset import AnnotatedDataset
from backend.task.cleaning.Imputation import Imputation
from backend.task.cleaning.DatasetCleaningStepExceptionHanding \
    import DatasetCleaningStepExceptionHandling as eh
from sklearn.impute import SimpleImputer


class ImputationMode(Imputation, ABC):
    """
    A cleaning_step for the dataset cleaning that removes missing values
    through the mode of the column.
    """

    def do_cleaning(self, dataset_to_clean: AnnotatedDataset) -> AnnotatedDataset:
        """
        Exchanges missing values through the mode. \n
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """

        # exception handling
        eh.check_non_none_column(dataset_to_clean.data, "ImputationMode")

        # Mode logic
        # normal case (more than one row)
        if len(dataset_to_clean.data.shape) > 1:
            # Replace None with np.nan
            dataset_to_clean.data = pd.DataFrame(dataset_to_clean.data).fillna(
                value=np.nan).to_numpy()
            # Use SimpleImputer to replace np.nan with None
            imputer_mode: SimpleImputer = SimpleImputer(missing_values=np.nan,
                                                        strategy='most_frequent')
            imputer_mode.fit(dataset_to_clean.data)
            AnnotatedDataset.data = imputer_mode.transform(dataset_to_clean.data)
            return dataset_to_clean

        # edge case handling: one row only
        else:
            return dataset_to_clean

