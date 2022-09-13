import shutil
import unittest
import os

import numpy
import numpy as np

from backend.AnnotatedDataset import AnnotatedDataset
from backend.DataIO import DataIO
from backend.DataIOInputException import DataIOInputException


class UnitTestDataIO(unittest.TestCase):
    _test_dir_path: str = os.path.join(os.getcwd(), "UnitTestDataIO_TestDir")

    def setUp(self) -> None:
        UnitTestDataIO._clean_dir(UnitTestDataIO._test_dir_path)
        os.makedirs(UnitTestDataIO._test_dir_path)

    def tearDown(self) -> None:
        UnitTestDataIO._clean_dir(UnitTestDataIO._test_dir_path)

    def test_annotated_ds_io(self):
        test_file_path: str = os.path.join(
            UnitTestDataIO._test_dir_path, "test_file_path"
        )
        with open(test_file_path, "w") as file:
            file.write("10,b,c,d\n1,gr,h,i\n4,l,m,n")

        anno_ds = DataIO.read_annotated(test_file_path, False)
        self.assertTrue(np.array_equal(anno_ds.row_mapping, np.array([1, 4])))
        exp_data = numpy.array([["gr", "h", "i"], ["l", "m", "n"]])
        self.assertTrue(np.array_equal(anno_ds.data, exp_data))
        self.assertTrue(np.array_equal(anno_ds.headers, np.array(["b", "c", "d"])))
        full_data = numpy.array(
            [[10, "b", "c", "d"], [1, "gr", "h", "i"], [4, "l", "m", "n"]], dtype=object
        )
        back_to_single = anno_ds.to_single_array()
        back_to_single[0][0] = 10
        self.assertTrue(np.array_equal(full_data, back_to_single))

        anno_ds = DataIO.read_annotated(test_file_path, False, False, False)
        self.assertTrue(np.array_equal(anno_ds.row_mapping, np.array([0, 1, 2])))
        self.assertTrue(np.array_equal(anno_ds.data, full_data))
        self.assertTrue(np.array_equal(anno_ds.headers, np.array(["0", "1", "2", "3"])))

    def test_read_uncleaned_csv_with_header(self):
        test_file_path: str = os.path.join(
            UnitTestDataIO._test_dir_path, "test_file_path"
        )
        with open(test_file_path, "w") as file:
            file.write("a,b,c,d,e\nf,g,h,i,j\nk,l,m,n,o")

        dataset: np.ndarray = DataIO.read_uncleaned_csv(test_file_path)

        self.assertTrue(
            np.array_equal(
                dataset,
                np.array([["f", "g", "h", "i", "j"], ["k", "l", "m", "n", "o"]]),
            )
        )

    def test_read_uncleaned_csv_without_header(self):
        test_file_path: str = os.path.join(
            UnitTestDataIO._test_dir_path, "test_file_path_headers"
        )
        with open(test_file_path, "w") as file:
            file.write("a,b,c,d,e\nf,g,h,i,j\nk,l,m,n,o")

        dataset: np.ndarray = DataIO.read_uncleaned_csv(test_file_path, has_header=None)

        self.assertTrue(
            np.array_equal(
                dataset,
                np.array(
                    [
                        ["a", "b", "c", "d", "e"],
                        ["f", "g", "h", "i", "j"],
                        ["k", "l", "m", "n", "o"],
                    ]
                ),
            )
        )

    def test_read_cleaned_csv_with_header(self):
        test_file_path: str = os.path.join(
            UnitTestDataIO._test_dir_path, "test_file_path_cleaned"
        )
        with open(test_file_path, "w") as file:
            file.write("a,b,c,d,e\n1,2,3,4,5\n6,7,8,9,10")

        dataset: np.ndarray = DataIO.read_cleaned_csv(test_file_path, has_header=0)

        # validate the values
        values: list[list[int]] = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]

        self.assertTrue(np.array_equal(dataset, values))

        # check that it is float32
        self.assertEqual(np.float32, dataset.dtype)

    def test_read_cleaned_csv_without_header(self):
        test_file_path: str = os.path.join(
            UnitTestDataIO._test_dir_path, "test_file_path_cleaned"
        )
        with open(test_file_path, "w") as file:
            file.write("12,21,23,56,45\n1,2,3,4,5\n6,7,8,9,10")

        dataset: np.ndarray = DataIO.read_cleaned_csv(test_file_path, has_header=None)

        # validate the values
        values: list[list[int]] = [
            [12, 21, 23, 56, 45],
            [1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10],
        ]

        self.assertTrue(np.array_equal(dataset, values))

        # check that it is float32
        self.assertEqual(np.float32, dataset.dtype)

    def test_read_error(self):
        test_file_path: str = os.path.join(
            UnitTestDataIO._test_dir_path, "test_file_path"
        )
        with open(test_file_path, "w") as file:
            file.write("a,b,c,d,e\nf,g,h,i,j\nk,l,m,n,o")

        with self.assertRaises(ValueError):
            DataIO.read_cleaned_csv(test_file_path)

    def test_invalid_file(self):
        test_file: str = "../resources/test/datasets/invalid_other_csv.csv"

        with self.assertRaises(DataIOInputException):
            DataIO.read_uncleaned_csv(test_file)

    def test_ads_opts(self):
        ads = AnnotatedDataset(np.array([[1]]), np.array(["a"]), np.array([0]))
        exp = np.array([["", "a"], [0, 1]], dtype=object)
        self.assertTrue(np.array_equal(ads.to_single_array(), exp))

    def test_write_csv(self):
        test_file_path: str = os.path.join(
            UnitTestDataIO._test_dir_path, "test_file_path"
        )

        array: np.array = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])
        nd_array: np.ndarray = np.ndarray(shape=(2, 5), dtype=int, buffer=array)

        # without header
        DataIO.write_csv(test_file_path, nd_array, has_header=False)

        with open(test_file_path, "r") as file:
            self.assertEqual(file.read(), "1,2,3,4,5\n6,7,8,9,10\n")

        # with header
        DataIO.write_csv(test_file_path, nd_array, has_header=True)

        with open(test_file_path, "r") as file:
            self.assertEqual(file.read(), "0,1,2,3,4\n1,2,3,4,5\n6,7,8,9,10\n")

    def test_save_write_csv(self):
        test_file_path_temp: str = os.path.join(
            UnitTestDataIO._test_dir_path, "test_file_path_temp"
        )
        test_file_path_final: str = os.path.join(
            UnitTestDataIO._test_dir_path, "test_file_path_final"
        )

        array: np.array = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])
        nd_array: np.ndarray = np.ndarray(shape=(2, 5), dtype=int, buffer=array)

        # without header
        DataIO.save_write_csv(
            test_file_path_temp, test_file_path_final, nd_array, has_header=False
        )

        with open(test_file_path_final, "r") as file:
            self.assertEqual(file.read(), "1,2,3,4,5\n6,7,8,9,10\n")

        self.assertFalse(os.path.isfile(test_file_path_temp))

        # with header
        DataIO.save_write_csv(
            test_file_path_temp, test_file_path_final, nd_array, has_header=True
        )

        with open(test_file_path_final, "r") as file:
            self.assertEqual(file.read(), "0,1,2,3,4\n1,2,3,4,5\n6,7,8,9,10\n")

        self.assertFalse(os.path.isfile(test_file_path_temp))

    # ---- static helper methods ----

    @staticmethod
    def _clean_dir(path: str):
        if os.path.isdir(path):
            shutil.rmtree(path)


if __name__ == "__main__":
    unittest.main()
