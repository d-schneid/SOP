from abc import ABC

import numpy as np
import pandas as pd
import sklearn

from backend_library.src.main.backend.task.cleaning.FeatureScaler import FeatureScaler


class MinMaxScaler(FeatureScaler, ABC):

    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        sklearn.preprocessing.minmax_scale(dataset_to_clean)
        df = pd.DataFrame(dataset_to_clean)
        return df.to_numpy()
