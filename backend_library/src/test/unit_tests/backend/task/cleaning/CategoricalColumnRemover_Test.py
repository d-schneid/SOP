import unittest

import numpy as np

from backend.task.cleaning.CategoricalColumnRemover import CategoricalColumnRemover as ccr
from test.DatasetsForTesting import Datasets as ds


class CategoricalColumnRemoverTest(unittest.TestCase):

    def setUp(self) -> None:
        self._ds: ds = ds()
        self._categorical_handler = ccr()

    def tearDown(self) -> None:
        self._min_max_scaler = None

    def test_categorical_column_remover(self):
        # Remove categorical data one row (edge case)
        cleaned_cat_dataset4: np.ndarray = np.asarray([1, 412, None])
        np.testing.assert_array_equal(cleaned_cat_dataset4,
                                      self._categorical_handler.do_cleaning(self._ds.cat_dataset4))

        # Remove Categorical data
        cleaned_cat_dataset1: np.ndarray = np.array([[-132., None], [0., None], [1., None]])
        np.testing.assert_array_equal(cleaned_cat_dataset1,
                                      self._categorical_handler.do_cleaning(self._ds.cat_dataset1))

        # All columns are categorical -> return empty array
        self.assertEqual(0, self._categorical_handler.do_cleaning(self._ds.cat_dataset2).size)

        # No categorical data -> Dont do anything
        np.testing.assert_array_equal(self._ds.dataset4,
                                      self._categorical_handler.do_cleaning(self._ds.dataset4))

        # No categorical data and some None values -> Dont do anything
        np.testing.assert_array_equal(self._ds.dataset1,
                                      self._categorical_handler.do_cleaning(self._ds.dataset1))

        # No categorical data and only None values -> Don't do anything
        np.testing.assert_array_equal(self._ds.none_dataset,
                                      self._categorical_handler.do_cleaning(self._ds.none_dataset))

        # Raise exception when empty dataset is inputted
        with self.assertRaises(ValueError) as context:
            self._categorical_handler.do_cleaning(self._ds.empty_dataset)


if __name__ == '__main__':
    unittest.main()
