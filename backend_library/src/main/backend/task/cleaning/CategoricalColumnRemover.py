from abc import ABC

import numpy as np
import pandas as pd

from backend_library.src.main.backend.task.cleaning.CategoricalDataHandler import CategoricalDataHandler


class CategoricalColumnRemover(CategoricalDataHandler, ABC):
    def __init__(self):
        pass

    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        df = pd.DataFrame(dataset_to_clean)
        return df.select_dtypes(exclude=['char']).to_numpy()
