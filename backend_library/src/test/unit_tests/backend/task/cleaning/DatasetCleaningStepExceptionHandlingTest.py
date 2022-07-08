import unittest

from backend.task.cleaning.DatasetCleaningStepExceptionHanding \
    import DatasetCleaningStepExceptionHandling as eh
from backend_library.src.test.DatasetsForTesting import Datasets as ds


class DatasetCleaningStepExceptionHandlingTest(unittest.TestCase):

    def setUp(self) -> None:
        self._ds: ds = ds()

    def test_check_non_empty_array(self):
        # Raise exception
        with self.assertRaises(ValueError) as context:
            eh.check_non_empty_array(self._ds.empty_dataset, "")

        # Dont raise exception
        try:
            eh.check_non_empty_array(self._ds.dataset0, "")
        except ValueError:
            self.fail("myFunc() raised ExceptionType unexpectedly!")

    def test_check_non_none_column(self):
        # Raise exception because None-column exists
        with self.assertRaises(ValueError) as context:
            eh.check_non_none_column(self._ds.none_dataset, "")

        # Raise exception because None-column exists
        with self.assertRaises(ValueError) as context:
            print(self._ds.dataset1)
            eh.check_non_none_column(self._ds.dataset1, "")

        # Dont raise exception
        try:
            eh.check_non_none_column(self._ds.dataset0, "")
        except ValueError:
            self.fail("myFunc() raised ExceptionType unexpectedly!")

        # Raise exception because no column exists
        with self.assertRaises(ValueError) as context:
            eh.check_non_none_column(self._ds.empty_dataset, "")


if __name__ == '__main__':
    unittest.main()
