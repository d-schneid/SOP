import unittest

import numpy as np

from backend.task.cleaning.DatasetCleaningStepExceptionHanding \
    import DatasetCleaningStepExceptionHandling as eh
from backend_library.resources.test.datasets.DatasetsForTesting import Datasets as ds


class UnitTestDatasetCleaningStepExceptionHandling(unittest.TestCase):
    _ds: ds = ds()

    def test_check_no_empty_array(self):
        # Raise exception
        with self.assertRaises(ValueError) as message:
            eh.check_no_empty_array(self._ds.empty_dataset, "root")
            self.assertEqual(message, "root: input array is empty. "
                                      "Needs at least one row, one column and an entry")

        # Dont raise exception
        try:
            eh.check_no_empty_array(self._ds.dataset0, "")
        except ValueError:
            self.fail("myFunc() raised ExceptionType unexpectedly!")

    def test_check_no_none_column(self):
        # Raise exception because None-column exists
        with self.assertRaises(ValueError):
            eh.check_no_none_column(self._ds.none_dataset, "")

        # Raise exception because None-column exists
        with self.assertRaises(ValueError):
            print(self._ds.dataset1)
            eh.check_no_none_column(self._ds.dataset1, "")

        # Dont raise exception
        try:
            eh.check_no_none_column(self._ds.dataset0, "")
        except ValueError:
            self.fail("myFunc() raised ExceptionType unexpectedly!")

        # Raise exception because no column exists
        with self.assertRaises(ValueError):
            eh.check_no_none_column(self._ds.empty_dataset, "")

        # edge case: Only one row with no None -> No Error
        self.assertIsNone(eh.check_no_none_column(np.asarray([1, 14, 15]), "ERROR"))

        # edge case: Only one row with None values -> Exception!
        with self.assertRaises(ValueError) as message:
            eh.check_no_none_column(np.asarray([None, 1, None, None, 14, 15, None]),
                                     "root")
            self.assertEqual(message, "root: None-column exists")


if __name__ == '__main__':
    unittest.main()
