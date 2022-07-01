from abc import ABC

import numpy as np
import pandas as pd

from backend_library.src.main.backend.task.cleaning.Imputation import Imputation


class ImputationMode(Imputation, ABC):

    def do_cleaning(self, dataset_to_clean: np.ndarray) -> np.ndarray:
        df = pd.DataFrame(dataset_to_clean)
        for column in df:
            df[column] = df[column].fillna(df[column].mean)
        return df.to_numpy()
