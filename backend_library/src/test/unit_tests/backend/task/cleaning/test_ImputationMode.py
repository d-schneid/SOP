import unittest

import numpy as np

from backend.task.cleaning.ImputationMode import ImputationMode
from test.DatasetsForTesting import Datasets as ds


class UnitTestImputationMode(unittest.TestCase):
    _ds: ds = ds()
    _mode: ImputationMode = ImputationMode()

    def test_imputation_mode(self):
        # use mode normally
        cleaned_dataset7: np.ndarray = \
            np.array([[-132., 7., 3.], [0., 7., 3.], [1., 7., 3.]])
        np.testing.assert_array_equal(cleaned_dataset7,
                                      self._mode.
                                      do_cleaning(self._ds.data_to_annotated
                                                  (self._ds.dataset7)).data)

        # No missing values -> Dont do anything
        np.testing.assert_array_equal(self._ds.dataset3,
                                       self._mode.
                                       do_cleaning(self._ds.data_to_annotated
                                                   (self._ds.dataset3)).data)

        # No missing values -> Dont do anything
        np.testing.assert_array_equal(self._ds.dataset4,
                                       self._mode.
                                       do_cleaning(self._ds.data_to_annotated
                                                   (self._ds.dataset4)).data)

        # Raise exception when empty dataset is inputted
        with self.assertRaises(ValueError):
            self._mode.do_cleaning(self._ds.data_to_annotated
                                   (self._ds.empty_dataset))

        # Raise exception when column with only None-values is inputted
        with self.assertRaises(ValueError):
            self._mode.do_cleaning(self._ds.data_to_annotated(self._ds.dataset1))

    def test_wrong_input_datatype(self):
        # 1D dataset not allowed -> Assertion
        with self.assertRaises(AssertionError):
            self._mode.do_cleaning(self._ds.one_dim_data_annotated)


if __name__ == '__main__':
    unittest.main()
