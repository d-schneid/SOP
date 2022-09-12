import os
import unittest

import pandas as pd

from backend.DatasetInfo import DatasetInfo
from test.DatasetsForTesting import Datasets as ds


class UnitTestDatasetInfo(unittest.TestCase):
    _dir_name: str = os.getcwd()
    _uncleaned_dataset_path1: str = os.path.join(_dir_name,
                                                 "uncleaned_dataset1.csv.error")
    _uncleaned_dataset_path2: str = os.path.join(_dir_name,
                                                 "uncleaned_dataset2.csv")
    _uncleaned_dataset_path3: str = os.path.join(_dir_name,
                                                 "uncleaned_dataset3.csv")

    _ds: ds = ds()

    def setUp(self) -> None:
        pd.DataFrame(self._ds.dataset0).to_csv(self._uncleaned_dataset_path1,
                                               index=False)

        pd.DataFrame(self._ds.empty_dataset).to_csv(self._uncleaned_dataset_path2,
                                                    index=False)

        pd.DataFrame(self._ds.none_dataset).to_csv(self._uncleaned_dataset_path3,
                                                   index=False)

    def tearDown(self) -> None:
        self.__clean_created_files_and_directories()

    def __clean_created_files_and_directories(self):
        if os.path.isfile(self._uncleaned_dataset_path1):
            os.remove(self._uncleaned_dataset_path1)
        if os.path.isfile(self._uncleaned_dataset_path2):
            os.remove(self._uncleaned_dataset_path2)
        if os.path.isfile(self._uncleaned_dataset_path3):
            os.remove(self._uncleaned_dataset_path3)

    def test_get_dataset_dimension(self):
        has_row_mapping: bool = True
        self.assertEqual(DatasetInfo.get_dataset_dimension
                         (self._uncleaned_dataset_path1, has_row_mapping), 2)
        self.assertEqual(DatasetInfo.get_dataset_dimension
                         (self._uncleaned_dataset_path2, has_row_mapping), 0)
        self.assertEqual(DatasetInfo.get_dataset_dimension
                         (self._uncleaned_dataset_path3, has_row_mapping), 4)

        has_row_mapping = False
        self.assertEqual(DatasetInfo.get_dataset_dimension
                         (self._uncleaned_dataset_path1, has_row_mapping), 3)
        self.assertEqual(DatasetInfo.get_dataset_dimension
                         (self._uncleaned_dataset_path2, has_row_mapping), 0)
        self.assertEqual(DatasetInfo.get_dataset_dimension
                         (self._uncleaned_dataset_path3, has_row_mapping), 5)

        self.__clean_created_files_and_directories()

    def test_get_dataset_datapoint_amount(self):
        has_header: bool = True
        self.assertEqual(DatasetInfo.get_dataset_datapoint_amount
                         (self._uncleaned_dataset_path1, has_header), 2)
        self.assertEqual(DatasetInfo.get_dataset_datapoint_amount
                         (self._uncleaned_dataset_path2, has_header), 0)
        self.assertEqual(DatasetInfo.get_dataset_datapoint_amount
                         (self._uncleaned_dataset_path3, has_header), 5)

        has_header = False
        self.assertEqual(DatasetInfo.get_dataset_datapoint_amount
                         (self._uncleaned_dataset_path1, has_header), 3)
        self.assertEqual(DatasetInfo.get_dataset_datapoint_amount
                         (self._uncleaned_dataset_path2, has_header), 0)
        self.assertEqual(DatasetInfo.get_dataset_datapoint_amount
                         (self._uncleaned_dataset_path3, has_header), 6)
        self.__clean_created_files_and_directories()

    # ---------- Tests for DatasetInfo.is_valid()
    csv_files_base_path = os.path.join(
        "..", "resources", "test", "datasets"
    )
    csv_file_invalid_edge_case = os.path.join(
        csv_files_base_path, "validator_invalid_edge_case.csv"
    )
    csv_file_inconsistent_col_nom = os.path.join(
        csv_files_base_path, "invalid_csv.csv"
    )
    csv_file_not_rfc_quote_char = os.path.join(
        csv_files_base_path, "non_rfc_conform.csv"
    )
    csv_file_rfc_linebreak = os.path.join(
        csv_files_base_path, "validator_rfc_linebreak.csv"
    )
    csv_file_valid = os.path.join(
        csv_files_base_path, "validator_valid.csv"
    )
    csv_file_cp1252 = os.path.join(
        csv_files_base_path, "validator_cp1252.csv"
    )

    def test_validation_edge_case(self):
        self.assertIsNotNone(
            DatasetInfo.is_dataset_valid(self.csv_file_invalid_edge_case)
        )

    def test_validation_inconsistent_column_number(self):
        self.assertIsNotNone(
            DatasetInfo.is_dataset_valid(self.csv_file_inconsistent_col_nom)
        )

    def test_validation_quote_char(self):
        self.assertIsNotNone(
            DatasetInfo.is_dataset_valid(self.csv_file_not_rfc_quote_char)
        )

    def test_validation_linebreak(self):
        self.assertIsNone(
            DatasetInfo.is_dataset_valid(self.csv_file_rfc_linebreak)
        )

    def test_validation_valid_csv(self):
        self.assertIsNone(
            DatasetInfo.is_dataset_valid(self.csv_file_valid)
        )

    def test_validation_unicode_error(self):
        self.assertIsNotNone(
            DatasetInfo.is_dataset_valid(self.csv_file_cp1252)
        )


if __name__ == '__main__':
    unittest.main()
