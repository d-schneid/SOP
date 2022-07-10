import numpy as np
import pandas as pd


class Datasets:

    @property
    def empty_dataset(self) -> np.ndarray:
        # create a numpy array that is empty

        #_df_empty: pd.DataFrame = pd.DataFrame({'empty': []})
        #return _df_empty.to_numpy()
        return np.zeros((0, 0))

    @property
    def none_dataset(self) -> np.ndarray:
        # create a numpy array that has only None-values
        _none_dataset: np.ndarray = np.empty((5, 5))
        _none_dataset[:] = np.NaN
        return _none_dataset

    @property
    def dataset0(self) -> np.ndarray:
        return np.zeros((2, 3))

    @property
    def dataset1(self) -> np.ndarray:
        return np.array([[-132., None, None], [0., 7., None], [1., 0., None]])

    @property
    def dataset2(self) -> np.ndarray:
        return np.array([[None, None, None, None, None], [0., 1., 0., 0., 4.], [0., 0., 1., 0., 2.]])

    @property
    def dataset3(self) -> np.ndarray:
        return np.array([[-1, 2], [-0.5, 6], [0, 2], [-1, 18]])

    @property
    def dataset4(self) -> np.ndarray:
        return np.array([[-213., 0., 541., 1., 0., 0., 4., 341.], [0., 0., 1., 0., 2., 1491., 213., 432.]])

    @property
    def dataset5(self) -> np.ndarray:
        return np.array([[-1, 2], [-0.5, 6], [0, 10], [1, 18]])

    @property
    def cat_dataset1(self) -> np.ndarray:
        return np.array([[-132., 'PSE', None], [0., 'IST', None], [1., 'SUPER', None]])

    @property
    def cat_dataset2(self) -> np.ndarray:
        return np.array([['Größter', 'PSE', 'fan'], [2., 0., None], [1., 99981., None]])

    @property
    def cat_dataset3(self) -> np.ndarray:
        return np.asarray([1, 412, "I am an evil String", None], object)
