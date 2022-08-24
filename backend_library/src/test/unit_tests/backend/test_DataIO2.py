import os.path
import unittest

import numpy as np

from backend.AnnotatedDataset import AnnotatedDataset
from backend.DataIO import DataIO
from backend.DataIOInputException import DataIOInputException


class UnitTestDataIO2(unittest.TestCase):
    _dataIO: DataIO = DataIO()

    # cleaned dataset 1
    _cleaned_dataset1_path: str = "./test/datasets/cleaned_dataset1.csv"
    _cleaned_data = np.asarray([[0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 1, 0.124, 1, 0.2, 0.14, 0.999999],
                                [0.42, 0.51, 0.1, 0.1324, 0.5198, 0.142, 0.5, 0.2]])
    _cleaned_annotated1: AnnotatedDataset = AnnotatedDataset(_cleaned_data,
                                                             None, None, True, True)

    # empty dataset
    _empty_dataset_path: str = "./test/datasets/empty_dataset.csv"

    # save write
    _save_write_path: str = "./test/datasets/save_write.csv"

    # save_convert_to_float 1D
    _to_convert_1D: np.ndarray = np.asarray([1, "2", "21.315", "Cannot be converted :(",
                                            "", 42, "25"])
    _converted_1D: np.ndarray = np.asarray([1.0, 2.0, 21.315, "Cannot be converted :(",
                                            "", 42.0, 25.0])

    def setUp(self) -> None:
        # cleanup
        self.cleanup_after_test()

    def test_read_already_cleaned_annotated_dataset(self):
        cleaned_dataset: AnnotatedDataset = \
            self._dataIO.read_annotated(self._cleaned_dataset1_path, True)
        np.testing.assert_array_equal(self._cleaned_annotated1.headers,
                                      cleaned_dataset.headers)
        np.testing.assert_array_almost_equal(self._cleaned_annotated1.data,
                                             cleaned_dataset.data)
        np.testing.assert_array_equal(self._cleaned_annotated1.row_mapping,
                                      cleaned_dataset.row_mapping)

        # cleanup
        self.cleanup_after_test()

    def test_read_uncleaned_csv_empty_dataset(self):
        # Raise exception when empty dataset is inputted
        with self.assertRaises(DataIOInputException):
            self._dataIO.read_uncleaned_csv(self._empty_dataset_path)

        # cleanup
        self.cleanup_after_test()

    def test_save_write_csv(self):
        self.assertFalse(os.path.isfile(self._save_write_path))

        # write data
        self._dataIO.save_write_csv(self._save_write_path + ".running",
                                    self._save_write_path, self._cleaned_data,
                                    True, True)

        # check if correct data is written
        cleaned_dataset: AnnotatedDataset = \
            self._dataIO.read_annotated(self._save_write_path, True)
        np.testing.assert_array_equal(self._cleaned_annotated1.headers,
                                      cleaned_dataset.headers)
        np.testing.assert_array_almost_equal(self._cleaned_annotated1.data,
                                             cleaned_dataset.data)
        np.testing.assert_array_equal(self._cleaned_annotated1.row_mapping,
                                      cleaned_dataset.row_mapping)

        # cleanup
        self.cleanup_after_test()

    def test_save_convert_to_float_one_dim(self):
        converted: np.ndarray = \
            self._dataIO._DataIO__save_convert_to_float(self._to_convert_1D)
        np.testing.assert_array_equal(self._converted_1D, converted)

    def cleanup_after_test(self):
        if os.path.isfile(self._save_write_path):
            os.remove(self._save_write_path)


if __name__ == '__main__':
    unittest.main()
