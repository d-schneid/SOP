import unittest

import numpy as np
import pandas as pd

from backend_library.src.main.backend.task.cleaning.ThresholdMissingValuesRemover import ThresholdMissingValuesRemover


class ThresholdMissingValuesRemoverTest(unittest.TestCase):
    def setUp(self) -> None:
        self._one_threshold_remover: ThresholdMissingValuesRemover = ThresholdMissingValuesRemover(threshold=1)
        self._zero_threshold_remover: ThresholdMissingValuesRemover = ThresholdMissingValuesRemover(threshold=0)
        self._half_threshold_remover: ThresholdMissingValuesRemover = ThresholdMissingValuesRemover(threshold=0.5)

        # create a numpy array that is empty
        df_empty: pd.DataFrame = pd.DataFrame({'empty': []})
        self._empty_dataset: np.ndarray = df_empty.to_numpy()

        # initialize all datasets for testing
        self._dataset0: np.ndarray = np.zeros((2, 3))
        self._dataset1: np.ndarray = np.array([[1., None, None], [0., 1., None], [1., 0., None]])
        self._dataset2: np.ndarray = \
            np.array([[None, None, None, None, None], [0., 1., 0., 0., 4.], [0., 0., 1., 0., 2.]])
        self._dataset3: np.ndarray = \
            np.array([[None, None, None, None, None], [None, None, None, None, None], [None, None, None, None, None]])

    def tearDown(self) -> None:
        self._one_threshold_remover = None
        self._zero_threshold_remover = None
        self._half_threshold_remover = None

    def test_threshold_value_one(self):
        """
        Tests ThresholdMissingValuesRemover with threshold 1 -> Remove all rows that have at least one None value.
        """
        # Array full of zeros -> remove Nothing
        cleaned_dataset0: np.ndarray = self._dataset0
        self.assertTrue(np.array_equal(cleaned_dataset0, self._one_threshold_remover.do_cleaning(self._dataset0)), True)

        # Every entry has one None value -> remove every row
        self.assertEqual(self._one_threshold_remover.do_cleaning(self._dataset1).shape[0], 0)

        # First row consists of only None values -> Remove first row
        cleaned_dataset2: np.ndarray = np.array([[0., 1., 0., 0., 4.], [0., 0., 1., 0., 2.]])
        self.assertTrue(np.array_equal(cleaned_dataset2, self._one_threshold_remover.do_cleaning(self._dataset2)), True)

        # All rows consists of only None values -> Remove all rows
        self.assertEqual(self._one_threshold_remover.do_cleaning(self._dataset3).shape[0], 0)

    def test_threshold_value_zero(self):
        """
        Tests ThresholdMissingValuesRemover with threshold 0 -> No rows are deleted
        """
        self.assertTrue(np.array_equal(self._dataset0, self._zero_threshold_remover.do_cleaning(self._dataset0)), True)
        self.assertTrue(np.array_equal(self._dataset1, self._zero_threshold_remover.do_cleaning(self._dataset1)), True)
        self.assertTrue(np.array_equal(self._dataset2, self._zero_threshold_remover.do_cleaning(self._dataset2)), True)
        self.assertTrue(np.array_equal(self._dataset3, self._zero_threshold_remover.do_cleaning(self._dataset3)), True)

    def test_threshold_half(self):
        """
        Tests ThresholdMissingValuesRemover with threshold 0.5 -> If a row has fewer values that are not None than
        the half of the amount of columns it gets removed.
        """
        # No None value -> remove Nothing
        cleaned_dataset0: np.ndarray = self._dataset0
        self.assertTrue(np.array_equal(cleaned_dataset0, self._half_threshold_remover.do_cleaning(self._dataset0)),
                        True)

        # First row has fewer than 2 values that are not None (and has 3 columns) -> remove first row
        cleaned_dataset1: np.ndarray = np.array([[0., 1., None], [1., 0., None]])
        self.assertTrue(np.array_equal(cleaned_dataset1, self._half_threshold_remover.do_cleaning(self._dataset1)),
                        True)

        # First row consists of only None values -> Remove first row
        cleaned_dataset2: np.ndarray = np.array([[0., 1., 0., 0., 4.], [0., 0., 1., 0., 2.]])
        self.assertTrue(np.array_equal(cleaned_dataset2, self._half_threshold_remover.do_cleaning(self._dataset2)),
                        True)

        # All rows consists of only None values -> Remove all rows
        self.assertEqual(self._half_threshold_remover.do_cleaning(self._dataset3).shape[0], 0)


if __name__ == '__main__':
    unittest.main()
