import unittest

import numpy as np

from backend.task.cleaning.MinMaxScaler import MinMaxScaler
from test.DatasetsForTesting import Datasets as ds


class UnitTestMinMaxScaler(unittest.TestCase):

    _ds: ds = ds()
    _min_max_scaler = MinMaxScaler()

    def test_min_max_scaler(self):
        # Test Min Max Scaling on normal array
        cleaned_dataset5: np.ndarray = np.array([[0., 0.], [0.25, 0.25], [0.5, 0.5], [1., 1.]])
        self.assertTrue(np.array_equal(cleaned_dataset5, self._min_max_scaler.do_cleaning(self._ds.dataset5), True))

        # Raise exception when empty dataset is inputted
        with self.assertRaises(ValueError) as context:
            self._min_max_scaler.do_cleaning(self._ds.empty_dataset)

        # Raise exception when column with only None-values is inputted
        with self.assertRaises(ValueError) as context:
            self._min_max_scaler.do_cleaning(self._ds.dataset1)

        # edge case: Only one row -> Replace each element with one
        np.testing.assert_array_equal(np.asarray([[1, 1, 1, 1, 1]]),
                                      self._min_max_scaler.do_cleaning(self._ds.dataset6))


if __name__ == '__main__':
    unittest.main()
