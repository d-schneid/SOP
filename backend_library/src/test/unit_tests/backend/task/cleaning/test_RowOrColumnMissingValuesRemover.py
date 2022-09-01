import unittest

import numpy as np

from backend.task.cleaning.RowOrColumnMissingValuesRemover import \
    RowOrColumnMissingValuesRemover
from backend_library.resources.test.datasets.DatasetsForTesting import Datasets as ds


class UnitTestRowMissingValuesRemover(unittest.TestCase):
    _ds: ds = ds()
    _row_remover: RowOrColumnMissingValuesRemover = RowOrColumnMissingValuesRemover(
        axis=0)

    def test_empty_array(self):
        # Raise exception when empty dataset is inputted
        with self.assertRaises(ValueError):
            self._row_remover.do_cleaning(self._ds.empty_annotated_dataset)

    def test_none_row_remove(self):
        # No missing values -> Don't change anything
        np.testing.assert_array_equal(self._ds.dataset0,
                                      self._row_remover.do_cleaning(
                                          self._ds.data_to_annotated(
                                              self._ds.dataset0)).data)

        # Missing values but no missing rows -> Don't change anything
        np.testing.assert_array_equal(self._ds.dataset1,
                                      self._row_remover.do_cleaning(
                                          self._ds.data_to_annotated(
                                              self._ds.dataset1)).data)

        # One row with missing values -> remove one row
        self._cleaned_dataset2 = np.array([[0., 1., 0., 0., 4.], [0., 0., 1., 0., 2.]])
        np.testing.assert_array_equal(self._cleaned_dataset2,
                                      self._row_remover.do_cleaning(
                                          self._ds.data_to_annotated(
                                              self._ds.dataset2)).data)

        # None array -> remove all rows (returns empty array)
        self.assertEqual(0, self._row_remover.do_cleaning(
            self._ds.data_to_annotated(self._ds.none_dataset))
                         .data.size)

        # Empty array -> throw exception
        with self.assertRaises(ValueError):
            self._row_remover.do_cleaning(self._ds.empty_annotated_dataset)

    def test_wrong_input_datatype(self):
        # 1D dataset not allowed -> Assertion
        with self.assertRaises(AssertionError):
            self._row_remover.do_cleaning(self._ds.one_dim_data_annotated)

    def test_wrong_axis(self):
        # only axis 0 or 1 allowed
        with self.assertRaises(ValueError):
            RowOrColumnMissingValuesRemover(axis=-1)
        with self.assertRaises(ValueError):
            RowOrColumnMissingValuesRemover(axis=-10000)
        with self.assertRaises(ValueError):
            RowOrColumnMissingValuesRemover(axis=2)
        with self.assertRaises(ValueError):
            RowOrColumnMissingValuesRemover(axis=3)
        with self.assertRaises(ValueError):
            RowOrColumnMissingValuesRemover(axis=100000)


class UnitTestColumnMissingValuesRemover(unittest.TestCase):
    _ds: ds = ds()
    _column_remover: RowOrColumnMissingValuesRemover = RowOrColumnMissingValuesRemover(
        axis=1)

    def test_none_columns_remove(self):
        # No missing values -> Don't change anything
        np.testing.assert_array_equal(self._ds.dataset0,
                                      self._column_remover.do_cleaning(
                                          self._ds.data_to_annotated(
                                              self._ds.dataset0)).data)

        # Missing values but no missing columns -> Don't change anything
        np.testing.assert_array_equal(self._ds.dataset2,
                                      self._column_remover.do_cleaning(
                                          self._ds.data_to_annotated(
                                              self._ds.dataset2)).data)

        # One column with missing values -> remove one column
        self._cleaned_dataset1 = np.array([[-132., None], [0., 7.], [1., 0.]])
        np.testing.assert_array_equal(self._cleaned_dataset1,
                                      self._column_remover.do_cleaning(
                                          self._ds.data_to_annotated(
                                              self._ds.dataset1)).data)

        # None array -> remove all columns (returns empty array)
        self.assertEqual(0,
                         self._column_remover.do_cleaning(self._ds.data_to_annotated
                         (self._ds.none_dataset))
                         .data.size)

        # Empty array -> throw exception
        with self.assertRaises(ValueError):
            self._column_remover.do_cleaning(self._ds.empty_annotated_dataset)


if __name__ == '__main__':
    unittest.main()
