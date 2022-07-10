import unittest

import numpy as np

from backend.task.cleaning.ImputationMode import ImputationMode
from backend_library.src.test.DatasetsForTesting import Datasets as ds


class ImputationModeTest(unittest.TestCase):

    def setUp(self) -> None:
        self._ds: ds = ds()
        self._mode: ImputationMode = ImputationMode()

    def test_imputation_mode(self):
        # use mode normally
        cleaned_dataset3: np.ndarray = np.array([[-1, 2], [-1, 2], [-1, 2], [-1, 2]])
        self.assertTrue(np.array_equal(self._ds.dataset3,
                                       self._mode.do_cleaning(self._ds.dataset3)), True)

        # No missing values -> Dont do anything
        self.assertTrue(np.array_equal(self._ds.dataset4,
                                       self._mode.do_cleaning(self._ds.dataset4)), True)

        # Raise exception when empty dataset is inputted
        with self.assertRaises(ValueError) as context:
            self._mode.do_cleaning(self._ds.empty_dataset)

        # Raise exception when column with only None-values is inputted
        with self.assertRaises(ValueError) as context:
            self._mode.do_cleaning(self._ds.dataset1)

        # edge case: Only one row -> Replace each element with one
        np.testing.assert_array_equal(np.asarray([[1, 1, 1, 1, 1]], np.float32),
                                      self._mode.do_cleaning(self._ds.dataset6))


if __name__ == '__main__':
    unittest.main()
