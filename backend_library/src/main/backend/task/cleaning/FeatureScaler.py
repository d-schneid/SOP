import numpy as np
from abc import ABC, abstractmethod

from backend_library.src.main.backend.task.cleaning.DatasetCleaningStep import DatasetCleaningStep


class FeatureScaler(DatasetCleaningStep, ABC):
    @abstractmethod
    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        return np.empty(0)
