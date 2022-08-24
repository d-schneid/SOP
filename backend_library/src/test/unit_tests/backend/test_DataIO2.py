import unittest

import numpy as np

from backend.AnnotatedDataset import AnnotatedDataset
from backend.DataIO import DataIO


class UnitTestDataIO2(unittest.TestCase):
    _dataIO: DataIO = DataIO()

    # cleaned dataset 1
    _cleaned_dataset1_path: str = "./test/datasets/cleaned_dataset1.csv"
    _cleaned_data = np.asarray([[0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 1, 0.124, 1, 0.2, 0.14, 0.999999],
                                [0.42, 0.51, 0.1, 0.1324, 0.5198, 0.142, 0.5, 0.2]])
    _cleaned_annotated1: AnnotatedDataset = AnnotatedDataset(_cleaned_data,
                                                             None, None, True, True)

    def test_read_already_cleaned_annotated_dataset(self):
        cleaned_dataset: AnnotatedDataset = \
            self._dataIO.read_annotated(self._cleaned_dataset1_path, True)
        np.testing.assert_array_equal(self._cleaned_annotated1.headers,
                                      cleaned_dataset.headers)
        np.testing.assert_array_almost_equal(self._cleaned_annotated1.data,
                                             cleaned_dataset.data)
        np.testing.assert_array_equal(self._cleaned_annotated1.row_mapping,
                                      cleaned_dataset.row_mapping)


if __name__ == '__main__':
    unittest.main()
