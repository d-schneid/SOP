import os

import numpy as np
import numpy.typing as npt
import pandas as pd


class DataIO:
    @staticmethod
    def read_cleaned_csv(path: str) -> np.ndarray:
        return DataIO.read_uncleaned_csv(path)
        # TODO: Test if csv-file consists of only float32. (Finn you could use astype if you want to for this)

    @staticmethod
    def read_uncleaned_csv(path: str) -> np.ndarray:
        assert os.path.isfile(path) is True

        df: pd.DataFrame = pd.read_csv(path)
        return df.to_numpy()

    @staticmethod
    def write_csv(path: str, data: np.ndarray):
        # TODO: Implement
        pass
