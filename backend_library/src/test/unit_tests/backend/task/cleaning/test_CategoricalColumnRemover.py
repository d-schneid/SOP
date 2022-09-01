import unittest

import numpy as np

from backend.task.cleaning.CategoricalColumnRemover \
    import CategoricalColumnRemover as ccr
from backend_library.resources.test.datasets.DatasetsForTesting import Datasets as ds


class UnitTestCategoricalColumnRemover(unittest.TestCase):
    _ds: ds = ds()
    _categorical_handler = ccr()

    def test_categorical_column_remover(self):
        # Remove Categorical data
        cleaned_cat_dataset1: np.ndarray = \
            np.array([[-132., None], [0., None], [1., None]])
        np.testing.assert_array_equal(cleaned_cat_dataset1,
                                      self._categorical_handler.
                                      do_cleaning(self._ds.data_to_annotated
                                                  (self._ds.cat_dataset1)).data)

        # All columns are categorical -> return empty array
        self.assertEqual(0,
                         self._categorical_handler.
                         do_cleaning(self._ds.data_to_annotated
                                     (self._ds.cat_dataset2)).data.size)

        # No categorical data -> Dont do anything
        np.testing.assert_array_equal(self._ds.dataset4,
                                      self._categorical_handler.
                                      do_cleaning(self._ds.data_to_annotated
                                                  (self._ds.dataset4)).data)

        # No categorical data and some None values -> Dont do anything
        np.testing.assert_array_equal(self._ds.dataset1,
                                      self._categorical_handler.
                                      do_cleaning(self._ds.data_to_annotated
                                                  (self._ds.dataset1)).data)

        # No categorical data and only None values -> Don't do anything
        self.assertEqual(self._ds.none_dataset.shape,
                         self._categorical_handler.
                         do_cleaning(self._ds.data_to_annotated
                                     (self._ds.none_dataset)).data.shape)

        # Raise exception when empty dataset is inputted
        with self.assertRaises(ValueError):
            self._categorical_handler.do_cleaning(self._ds.empty_annotated_dataset)

    def test_wrong_input_datatype(self):
        # 1D dataset not allowed -> Assertion
        with self.assertRaises(AssertionError):
            self._categorical_handler.do_cleaning(self._ds.one_dim_data_annotated)


if __name__ == '__main__':
    unittest.main()
