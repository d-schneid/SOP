import os
import unittest

import numpy as np
import pandas as pd

from backend.DataInfo import DataInfo

from backend_library.src.test.DatasetsForTesting import Datasets as ds


class DataInfoTest(unittest.TestCase):
    dir_name: str = os.getcwd()
    uncleaned_dataset_path1: str = os.path.join(dir_name, "uncleaned_dataset1.csv")
    uncleaned_dataset_path2: str = os.path.join(dir_name, "uncleaned_dataset2.csv")
    uncleaned_dataset_path3: str = os.path.join(dir_name, "uncleaned_dataset3.csv")

    def setUp(self) -> None:
        self._ds: ds = ds()

        pd.DataFrame(self._ds.dataset0).to_csv(self.uncleaned_dataset_path1, index=False)

        pd.DataFrame(self._ds.empty_dataset).to_csv(self.uncleaned_dataset_path2, index=False)

        pd.DataFrame(self._ds.none_dataset).to_csv(self.uncleaned_dataset_path3, index=False)

        print(self._ds.empty_dataset.shape)

    def tearDown(self) -> None:
        if os.path.isfile(self.uncleaned_dataset_path1):
            os.remove(self.uncleaned_dataset_path1)
        if os.path.isfile(self.uncleaned_dataset_path2):
            os.remove(self.uncleaned_dataset_path2)
        if os.path.isfile(self.uncleaned_dataset_path3):
            os.remove(self.uncleaned_dataset_path3)
        self._ds = None

    def test_get_dataset_dimension(self):
        self.assertEqual(DataInfo.get_dataset_dimension(self.uncleaned_dataset_path1), 3)
        self.assertEqual(DataInfo.get_dataset_dimension(self.uncleaned_dataset_path2), 0)
        self.assertEqual(DataInfo.get_dataset_dimension(self.uncleaned_dataset_path3), 5)

    def test_get_dataset_datapoint_amount(self):
        self.assertEqual(DataInfo.get_dataset_datapoint_amount(self.uncleaned_dataset_path1), 2)
        self.assertEqual(DataInfo.get_dataset_datapoint_amount(self.uncleaned_dataset_path2), 0)
        self.assertEqual(DataInfo.get_dataset_datapoint_amount(self.uncleaned_dataset_path3), 5)


if __name__ == '__main__':
    unittest.main()
