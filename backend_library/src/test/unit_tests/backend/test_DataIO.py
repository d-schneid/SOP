import math
import shutil
import unittest
import os

import numpy
import numpy as np
from typing import List

from backend import DataIO


class UnitTestDataIO(unittest.TestCase):
    _test_dir_path: str = os.path.join(os.getcwd(), "UnitTestDataIO_TestDir")

    def setUp(self) -> None:
        UnitTestDataIO._clean_dir(UnitTestDataIO._test_dir_path)
        os.makedirs(UnitTestDataIO._test_dir_path)

    def tearDown(self) -> None:
        UnitTestDataIO._clean_dir(UnitTestDataIO._test_dir_path)

    def test_annotated_ds_io(self):
        test_file_path: str = os.path.join(UnitTestDataIO._test_dir_path,
                                           "test_file_path")
        with open(test_file_path, "w") as file:
            file.write("10,b,c,d\n1,gr,h,i\n4,l,m,n")

        anno_ds = DataIO.DataIO.read_with_annotated(test_file_path, False)
        self.assertTrue(np.array_equal(anno_ds.row_mapping, np.array([1, 4])))
        exp_data = numpy.array([["gr", "h", "i"], ["l", "m", "n"]])
        self.assertTrue(np.array_equal(anno_ds.data, exp_data))
        self.assertTrue(np.array_equal(anno_ds.headers, np.array(["b", "c", "d"])))
        full_data = numpy.array(
            [[10, "b", "c", "d"], [1, "gr", "h", "i"], [4, "l", "m", "n"]],
            dtype=object)
        back_to_single = anno_ds.to_single_array()
        back_to_single[0][0] = 10
        self.assertTrue(np.array_equal(full_data, back_to_single))

        anno_ds = DataIO.DataIO.read_with_annotated(test_file_path, False, False, False)
        self.assertTrue(np.array_equal(anno_ds.row_mapping, np.array([0, 1, 2])))
        self.assertTrue(np.array_equal(anno_ds.data, full_data))
        self.assertTrue(np.array_equal(anno_ds.headers, np.array(["0", "1", "2", "3"])))

    def test_read_uncleaned_csv(self):
        test_file_path: str = os.path.join(UnitTestDataIO._test_dir_path,
                                           "test_file_path")
        with open(test_file_path, "w") as file:
            file.write("a,b,c,d,e\nf,g,h,i,j\nk,l,m,n,o")

        dataset: np.ndarray = DataIO.DataIO.read_uncleaned_csv(test_file_path)

        self.assertEqual(str(dataset),
                         "[['f' 'g' 'h' 'i' 'j']\n ['k' 'l' 'm' 'n' 'o']]")

        # TODO

    def test_read_cleaned_csv(self):
        test_file_path: str = os.path.join(UnitTestDataIO._test_dir_path, "test_file_path")
        with open(test_file_path, "w") as file:
            file.write("a,b,c,d,e\n1,2,3,4,5\n6,7,8,9,10")

        dataset: np.ndarray = DataIO.DataIO.read_cleaned_csv(test_file_path, has_header=0)

        # validate the values
        values: List[List[int]] = [[1,2,3,4,5], [6,7,8,9,10]]

        for i in range(dataset.shape[0]):
            for k in range(dataset.shape[1]):
                self.assertTrue(math.isclose(values[i][k], dataset[i][k]))

        # TODO

    def test_read_error(self):
        test_file_path: str = os.path.join(UnitTestDataIO._test_dir_path, "test_file_path")
        with open(test_file_path, "w") as file:
            file.write("a,b,c,d,e\nf,g,h,i,j\nk,l,m,n,o")

        with self.assertRaises(ValueError):
            dataset: np.ndarray = DataIO.DataIO.read_cleaned_csv(test_file_path)

        # TODO

    def test_write_csv(self):
        test_file_path: str = os.path.join(UnitTestDataIO._test_dir_path, "test_file_path")

        array: np.array =  np.array([[1,2,3,4,5], [6,7,8,9,10]])
        nd_array: np.ndarray = np.ndarray(shape=(2,5), dtype=int, buffer=array)

        DataIO.DataIO.write_csv(test_file_path, nd_array, has_header=True)

        # check the written data
        with open(test_file_path) as file:
            file.readline()
            self.assertEqual(file.read(), "1,2,3,4,5\n6,7,8,9,10\n")

        # TODO

    # ---- static helper methods ----

    @staticmethod
    def _clean_dir(path: str):
        if os.path.isdir(path):
            shutil.rmtree(path)

if __name__ == '__main__':
    unittest.main()
