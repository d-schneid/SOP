import unittest

import numpy as np

from backend.task.cleaning.MinMaxScaler import MinMaxScaler
from test.DatasetsForTesting import Datasets as ds


class UnitTestMinMaxScaler(unittest.TestCase):
    _ds: ds = ds()
    _min_max_scaler = MinMaxScaler()

    def test_min_max_scaler(self):
        # Test Min Max Scaling on normal array
        cleaned_dataset5: np.ndarray = np.array(
            [[0., 0.], [0.25, 0.25], [0.5, 0.5], [1., 1.]])
        np.testing.assert_array_equal(cleaned_dataset5,
                                      self._min_max_scaler.
                                      do_cleaning(self._ds.data_to_annotated
                                                  (self._ds.dataset5)).data)

        # Raise exception when empty dataset is inputted
        with self.assertRaises(ValueError) as context:
            self._min_max_scaler.do_cleaning(self._ds.empty_annotated_dataset)

        # Raise exception when column with only None-values is inputted
        with self.assertRaises(ValueError) as context:
            self._min_max_scaler \
                .do_cleaning(self._ds.data_to_annotated(self._ds.dataset1))

        # edge case: Only one row -> Replace each element with zero
        np.testing.assert_array_equal(np.asarray([[0, 0, 0, 0, 0]]),
                                      self._min_max_scaler.
                                      do_cleaning(self._ds.data_to_annotated
                                                  (self._ds.dataset6)).data)

    def test_wrong_input_datatype(self):
        # 1D dataset not allowed -> Assertion
        with self.assertRaises(AssertionError) as context:
            self._min_max_scaler.do_cleaning(self._ds.one_dim_data_annotated)


if __name__ == '__main__':
    unittest.main()
