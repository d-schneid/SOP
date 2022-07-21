import os
import shutil
import unittest

import numpy as np

from backend.metric.ExecutionElementMetricHelper import ExecutionElementMetricHelper
from backend.DataIO import DataIO


class UnitTest_ExecutionElementMetricHelper(unittest.TestCase):
    _dir_path: str = os.getcwd() + "\\test\\unit_tests\\backend\\metric"
        #os.path.join(os.path.join(os.path.join(
                    #os.path.join(os.getcwd(), "test"), "unit_test"), "backend"), "metric")


    _csv_to_store: np.ndarray = np.asarray([[42]])

    _csv_paths_in_this_directory: list[str] = list([os.path.join(_dir_path, "first.csv")])

    _child_directory: str = os.path.join(_dir_path, "child_directory")
    _csv_paths_in_child_directory: list[str] = list([os.path.join(_child_directory, "first.csv")])

    _error_csv_path: str = os.path.join(_dir_path, "this_element_failed.csv.error")

    def setUp(self) -> None:
        self.__clean_existing_files()

    def test_GetExecutionElementsResultPaths(self):
        # No .csv files
        self.assertEqual(len(ExecutionElementMetricHelper.GetExecutionElementsResultPaths(self._dir_path)), 0)

        # csv files in this directory
        for i in range(0, len(self._csv_paths_in_this_directory)):
            DataIO.write_csv(self._csv_paths_in_this_directory[i], self._csv_to_store)
            self.assertEqual(len(ExecutionElementMetricHelper.GetExecutionElementsResultPaths(self._dir_path)), i+1)

        # ignore error files
        DataIO.write_csv(self._error_csv_path, self._csv_to_store)
        self.assertEqual(len(ExecutionElementMetricHelper.GetExecutionElementsResultPaths(self._dir_path)),
                         len(self._csv_paths_in_this_directory))

        # csv files in child directory
        os.mkdir(self._child_directory)
        for i in range(0, len(self._csv_paths_in_child_directory)):
            DataIO.write_csv(self._csv_paths_in_child_directory[i], self._csv_to_store)
            self.assertEqual(len(ExecutionElementMetricHelper.GetExecutionElementsResultPaths(self._dir_path)),
                             len(self._csv_paths_in_this_directory)+i+1)

        self.__clean_existing_files()

    def __clean_existing_files(self):
        if os.path.isdir(self._child_directory):
            shutil.rmtree(self._child_directory)

        for path in self._csv_paths_in_this_directory:
            if os.path.isfile(path):
                os.remove(path)

        if os.path.isfile(self._error_csv_path):
            os.remove(self._error_csv_path)


if __name__ == '__main__':
    unittest.main()
