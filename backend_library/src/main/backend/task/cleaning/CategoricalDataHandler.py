import numpy as np
from abc import ABC, abstractmethod

from backend_library.src.main.backend.task.cleaning.DatasetCleaningStep import DatasetCleaningStep


class CategoricalDataHandler(DatasetCleaningStep, ABC):
    """
    Divides DatasetCleaningStep into the logical part that focuses on handling categorical datasets.
    """
    @abstractmethod
    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        """
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        return np.empty(0)
