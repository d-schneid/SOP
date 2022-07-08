import numpy as np
from abc import ABC, abstractmethod


class DatasetCleaningStep(ABC):
    """
    Every cleaning_step of the cleaning_pipeline has to implement this abstract class.
    """
    @abstractmethod
    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        """
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        return np.empty(0)
