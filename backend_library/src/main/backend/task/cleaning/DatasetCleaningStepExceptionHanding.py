import numpy as np
import pandas as pd


class DatasetCleaningStepExceptionHandling:
    """
    Offers static checks for the DatasetCleaningSteps that throw corresponding exceptions on error.
    """

    @staticmethod
    def check_non_empty_array(dataset_to_check: np.ndarray, error_root: str) -> None:
        """
        :param dataset_to_check: 2D-array that should be checked.
        :param error_root: Will be displayed as the error root in the error message. (error_root: error_message)
        :return: Throws an ValueError exception if the inputted dataset is empty
        """
        if dataset_to_check.size == 0 or dataset_to_check.shape[0] == 0 or dataset_to_check.shape[1] == 0:
            raise ValueError(error_root + ": input array is empty. Needs at least one row, one column and an entry")

    @staticmethod
    def check_non_none_column(dataset_to_check: np.ndarray, error_root: str) -> None:
        """
        :param dataset_to_check: 2D-array that should be checked.
        :param error_root: Will be displayed as the error root in the error message. (error_root: error_message)
        :return: Throws an ValueError exception if the inputted dataset has one None-column (or has no entries at all)
        """
        DatasetCleaningStepExceptionHandling.check_non_empty_array(dataset_to_check, error_root)

        for column_idx in range(0, dataset_to_check.shape[1]):
            df: pd.DataFrame = pd.DataFrame(dataset_to_check[:, column_idx])
            is_none_array: np.ndarray = df.isna().to_numpy()
            if is_none_array.all():
                raise ValueError(error_root + ": None-column exists")
