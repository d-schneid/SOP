import numpy as np
from abc import ABC, abstractmethod


class DatasetCleaningStep(ABC):
    @abstractmethod
    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        return np.empty(0)
