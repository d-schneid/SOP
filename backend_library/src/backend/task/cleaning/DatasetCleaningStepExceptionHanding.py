import numpy as np
import pandas as pd
from backend.DatasetInfo import DatasetInfo


class DatasetCleaningStepExceptionHandling:
    """
    Offers static checks for the DatasetCleaningSteps
    that throw corresponding exceptions on error.
    """

    @staticmethod
    def check_non_empty_array(dataset_to_check: np.ndarray, error_root: str) -> None:
        """
        :param dataset_to_check: 2D-array that should be checked.
        :param error_root: Will be displayed as the error root in the error message.
        (error_root: error_message)
        :return: Throws an ValueError exception if the inputted dataset is empty
        """
        try:
            if dataset_to_check.size == 0:
                raise ValueError(error_root +
                                 ": input array is empty. Needs at least one row, "
                                 "one column and an entry")
        except pd.errors.EmptyDataError:
            raise ValueError(error_root +
                             ": input array is empty. Needs at least one row, "
                             "one column and an entry")

    @staticmethod
    def check_non_none_column(dataset_to_check: np.ndarray, error_root: str) -> None:
        """
        :param dataset_to_check: 2D-array that should be checked.
        :param error_root: Will be displayed as the error root in the error message.
        (error_root: error_message)
        :return: Throws an ValueError exception if the inputted dataset
        has one None-column (or has no entries at all)
        """
        DatasetCleaningStepExceptionHandling.check_non_empty_array(dataset_to_check,
                                                                   error_root)

        # normal case (more than one row)
        if len(dataset_to_check.shape) > 1:
            for column_idx in range(0, dataset_to_check.shape[1]):
                df: pd.DataFrame = pd.DataFrame(dataset_to_check[:, column_idx])
                is_none_array: np.ndarray = df.isna().to_numpy()
                if is_none_array.all():
                    raise ValueError(error_root + ": None-column exists")
        # edge case handling: one row only
            else:
                for idx in range(0, dataset_to_check.shape[0]):
                    if str(type(dataset_to_check[idx])) == '<class \'NoneType\'>':
                        raise ValueError(error_root + ": None-column exists")
