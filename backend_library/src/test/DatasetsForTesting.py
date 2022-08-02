import numpy as np
import pandas as pd

from backend.AnnotatedDataset import AnnotatedDataset


class Datasets:

    @property
    def empty_dataset(self) -> np.ndarray:
        # create a numpy array that is empty
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
    def dataset6(self) -> np.ndarray:
        return np.array([-1, 1234, 12, 53, 6])

    @property
    def dataset7(self) -> np.ndarray:
        return np.array([[-132., None, None], [0., 7., None], [1., 7., 3.]])

    @property
    def cat_dataset1(self) -> np.ndarray:
        return np.array([[-132., 'PSE', None], [0., 'IST', None], [1., 'SUPER', None]])

    @property
    def cat_dataset2(self) -> np.ndarray:
        return np.array([['Größter', 'PSE', 'fan'], [2., 0., None], [1., 99981., None]])

    @property
    def cat_dataset3(self) -> np.ndarray:
        return np.asarray([[1, 412, "I am an evil String", None]], object)

    @property
    def cat_dataset4(self) -> np.ndarray:
        return np.asarray([1, 412, "I am an evil String", None], object)  # 1 dim array

    @property
    def mixed_dataset1(self) -> np.ndarray:
        return np.asarray([[1, 412, "I am an evil String", None]], object)

    @property
    def big_dataset1(self) -> np.ndarray:
        return np.array([[-1, 1234, 12, 53, 6, 124, None, 151245124, 1541],
                         [214123, 1, 21, None, 1241, "Eve the evil String", None, 213, -124512],
                         [12, -1234, None, 1, 15215, 4, None, 12, 12],
                         [None, None, None, None, None, None, None, None, None],
                         [12, -1234, None, 1, 15215, 4, None, 12, 12]])

    @property
    def system_test1(self) -> np.ndarray:
        return np.asarray([[0, 1, 2, 3], [1, 412, "I am an evil String", None]], object)

    @property
    def system_test2(self) -> np.ndarray:
        return np.array([[0, 1, 2, 3, 4, 5, 6, 7, 8],
                         [-1, 1234, 12, 53, 6, 124, None, 151245124, 1541],
                         [214123, 1, 21, None, 1241, "Eve the evil String", None, 213, -124512],
                         [12, -1234, None, 1, 15215, 4, None, 12, 12],
                         [None, None, None, None, None, None, None, None, None],
                         [12, -1234, None, 1, 15215, 4, None, 12, 12]])

    @property
    def one_dim_data_annotated(self) -> AnnotatedDataset:
        one_dim_data_annotated: AnnotatedDataset = \
            self.data_to_annotated(np.zeros((1, 1)))
        one_dim_data_annotated.data = np.zeros(1)
        return one_dim_data_annotated

    @property
    def empty_annotated_dataset(self) -> AnnotatedDataset:
        empty_annotated_dataset: AnnotatedDataset = \
            self.data_to_annotated(np.zeros((1, 1)))
        empty_annotated_dataset.data = self.empty_dataset
        return empty_annotated_dataset

    @staticmethod
    def data_to_annotated(data: np.ndarray):
        return AnnotatedDataset(data, generate_headers=True, generate_row_numbers=True)
