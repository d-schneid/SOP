import math
import shutil
import unittest
import os
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

    def test_read_uncleaned_csv(self):
        test_file_path: str = os.path.join(UnitTestDataIO._test_dir_path, "test_file_path")
        with open(test_file_path, "w") as file:
            file.write("a,b,c,d,e\nf,g,h,i,j\nk,l,m,n,o")

        dataset: np.ndarray = DataIO.DataIO.read_uncleaned_csv(test_file_path)

        self.assertEqual(str(dataset), "[['f' 'g' 'h' 'i' 'j']\n ['k' 'l' 'm' 'n' 'o']]")

        # TODO

    def test_read_cleaned_csv(self):
        test_file_path: str = os.path.join(UnitTestDataIO._test_dir_path, "test_file_path")
        with open(test_file_path, "w") as file:
            file.write("a,b,c,d,e\n1,2,3,4,5\n6,7,8,9,10")

        dataset: np.ndarray = DataIO.DataIO.read_cleaned_csv(test_file_path)

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

    # ---- static helper methods ----

    @staticmethod
    def _clean_dir(path: str):
        if os.path.isdir(path):
            shutil.rmtree(path)

if __name__ == '__main__':
    unittest.main()
