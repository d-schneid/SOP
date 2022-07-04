import numpy as np
import pandas as pd


class Datasets:
    _dataset0: np.ndarray = np.zeros((2, 3))
    _dataset1: np.ndarray = np.array([[-132., None, None], [0., 7., None], [1., 0., None]])
    _dataset2: np.ndarray = \
        np.array([[None, None, None, None, None], [0., 1., 0., 0., 4.], [0., 0., 1., 0., 2.]])
    _dataset3: np.ndarray = \
        np.array([[None, None, None, None, None], [None, None, None, None, None], [None, None, None, None, None]])
    _dataset4: np.ndarray = np.array([[-213., 0., 541., 1., 0., 0., 4., 341.], [0., 0., 1., 0., 2., 1491., 213., 432.]])
    _dataset5: np.ndarray = np.array([[-1, 2], [-0.5, 6], [0, 10], [1, 18]])

    # create a numpy array that is empty
    _df_empty: pd.DataFrame = pd.DataFrame({'empty': []})
    _empty_dataset: np.ndarray = _df_empty.to_numpy()

    @property
    def empty_dataset(self) -> np.ndarray:
        return self._empty_dataset

    @property
    def dataset0(self) -> np.ndarray:
        return self._dataset0

    @property
    def dataset1(self) -> np.ndarray:
        return self._dataset1

    @property
    def dataset2(self) -> np.ndarray:
        return self._dataset2

    @property
    def dataset3(self) -> np.ndarray:
        return self._dataset3
