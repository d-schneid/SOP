import numpy as np
from abc import ABC, abstractmethod

from backend.task.cleaning.DatasetCleaningStep import DatasetCleaningStep


class MissingValuesRemover(DatasetCleaningStep, ABC):
    """
    Divides DatasetCleaningStep into the logical part that focuses on deleting rows with to many missing values.
    """
    @abstractmethod
    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        """
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        return np.empty(0)
