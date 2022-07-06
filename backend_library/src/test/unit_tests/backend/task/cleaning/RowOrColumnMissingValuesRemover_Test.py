import unittest

import numpy as np

from backend_library.src.main.backend.task.cleaning.RowOrColumnMissingValuesRemover import \
    RowOrColumnMissingValuesRemover
from backend_library.src.test.unit_tests.backend.DatasetsForTesting import Datasets as ds


class RowThresholdMissingValuesRemoverTest(unittest.TestCase):
    def setUp(self) -> None:
        self._ds: ds = ds()
        self._row_remover: RowOrColumnMissingValuesRemover = RowOrColumnMissingValuesRemover(axis=0)

    def tearDown(self) -> None:
        self._row_zero_threshold_remover = None
        self._row_one_threshold_remover = None

    def test_empty_array(self):
        # Raise exception when empty dataset is inputted
        with self.assertRaises(ValueError) as context:
            self._row_remover.do_cleaning(self._ds.empty_dataset)

    def test_none_row_remove(self):
        # No missing values -> Don't change anything
        np.testing.assert_array_equal(self._ds.dataset0,
                                      self._row_remover.do_cleaning(self._ds.dataset0))

        # Missing values but no missing rows -> Don't change anything
        np.testing.assert_array_equal(self._ds.dataset1,
                                      self._row_remover.do_cleaning(self._ds.dataset1))

        # One row with missing values -> remove one row
        self._cleaned_dataset2 = np.array([[0., 1., 0., 0., 4.], [0., 0., 1., 0., 2.]])
        np.testing.assert_array_equal(self._cleaned_dataset2,
                                      self._row_remover.do_cleaning(self._ds.dataset2))

        # None array -> remove all rows (returns empty array)
        self.assertEqual(0, self._row_remover.do_cleaning(self._ds.none_dataset).size)

        # Empty array -> throw exception
        with self.assertRaises(ValueError) as context:
            self._row_remover.do_cleaning(self._ds.empty_dataset)


class ColumnThresholdMissingValuesRemoverTest(unittest.TestCase):
    def setUp(self) -> None:
        self._ds: ds = ds()
        self._column_remover: RowOrColumnMissingValuesRemover = RowOrColumnMissingValuesRemover(axis=1)

    def tearDown(self) -> None:
        self._row_zero_threshold_remover = None
        self._row_one_threshold_remover = None

    def test_none_row_remove(self):
        # No missing values -> Don't change anything
        np.testing.assert_array_equal(self._ds.dataset0,
                                      self._column_remover.do_cleaning(self._ds.dataset0))

        # Missing values but no missing columns -> Don't change anything
        np.testing.assert_array_equal(self._ds.dataset2,
                                      self._column_remover.do_cleaning(self._ds.dataset2))

        # One column with missing values -> remove one column
        self._cleaned_dataset1 = np.array([[-132., None], [0., 7.], [1., 0.]])
        np.testing.assert_array_equal(self._cleaned_dataset1,
                                      self._column_remover.do_cleaning(self._ds.dataset1))

        # None array -> remove all columns (returns empty array)
        self.assertEqual(0, self._column_remover.do_cleaning(self._ds.none_dataset).size)

        # Empty array -> throw exception
        with self.assertRaises(ValueError) as context:
            self._column_remover.do_cleaning(self._ds.empty_dataset)


if __name__ == '__main__':
    unittest.main()
