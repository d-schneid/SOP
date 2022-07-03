from abc import ABC

import numpy as np
import pandas as pd

from backend_library.src.main.backend.task.cleaning.CategoricalDataHandler import CategoricalDataHandler


class CategoricalColumnRemover(CategoricalDataHandler, ABC):
    """
    A cleaning_step for the dataset cleaning that removes all columns that contain categorical data.
    """

    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        """
        Remove all columns that contain categorical data. \n
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        df = pd.DataFrame(dataset_to_clean)
        return df.select_dtypes(exclude=['char']).to_numpy()
