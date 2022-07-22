import os
import shutil
import unittest

import numpy as np

from backend.metric.ExecutionElementMetricHelper import ExecutionElementMetricHelper
from backend.DataIO import DataIO


class UnitTest_ExecutionElementMetricHelper(unittest.TestCase):
    _dir_path: str = os.path.join(os.path.join(os.path.join(
        os.path.join(os.getcwd(), "test"), "unit_test"), "backend"), "metric")
    # + "\\test\\unit_tests\\backend\\metric"

    _csv_to_store: np.ndarray = np.asarray([[42]])

    _csv_paths_in_this_directory: list[str] = list([os.path.join(_dir_path, "first.csv"),
                                                    os.path.join(_dir_path, "second.csv"),
                                                    os.path.join(_dir_path, "random_name.csv")])

    _child_directory: str = os.path.join(_dir_path, "child_directory")
    _csv_paths_in_child_directory: list[str] = list([os.path.join(_child_directory, "first.csv"),
                                                     os.path.join(_child_directory, "second.csv"),
                                                     os.path.join(_child_directory, "random_name.csv")])

    _child_directory2: str = os.path.join(_dir_path, "child_directory2")
    _csv_paths_in_child_directory2: list[str] = list([os.path.join(_child_directory2, "first.csv"),
                                                      os.path.join(_child_directory2, "second.csv"),
                                                      os.path.join(_child_directory2, "random_name.csv")])

    _child_directory3: str = os.path.join(_dir_path, "child_directory3")
    _csv_paths_in_child_directory3: list[str] = list([os.path.join(_child_directory3, "first.csv"),
                                                      os.path.join(_child_directory3, "second.csv"),
                                                      os.path.join(_child_directory3, "random_name.csv")])

    _error_csv_path: str = os.path.join(_dir_path, "this_element_failed.csv.error")

    def setUp(self) -> None:
        self.__clean_existing_files()

    def test_get_csv_files_in_directory(self):
        # No .csv files
        self.assertEqual(len(ExecutionElementMetricHelper.
                             _ExecutionElementMetricHelper__get_csv_files_in_directory(self._dir_path)), 0)

        # csv files in this directory
        for i in range(0, len(self._csv_paths_in_this_directory)):
            DataIO.write_csv(self._csv_paths_in_this_directory[i], self._csv_to_store)
            self.assertEqual(len(ExecutionElementMetricHelper.
                                 _ExecutionElementMetricHelper__get_csv_files_in_directory(self._dir_path)), i + 1)

        # ignore error files
        DataIO.write_csv(self._error_csv_path, self._csv_to_store)
        self.assertEqual(len(ExecutionElementMetricHelper.
                             _ExecutionElementMetricHelper__get_csv_files_in_directory(self._dir_path)),
                         len(self._csv_paths_in_this_directory))

        # csv files in child directory
        os.mkdir(self._child_directory)
        for i in range(0, len(self._csv_paths_in_child_directory)):
            DataIO.write_csv(self._csv_paths_in_child_directory[i], self._csv_to_store)
            self.assertEqual(len(ExecutionElementMetricHelper.
                                 _ExecutionElementMetricHelper__get_csv_files_in_directory(self._dir_path)),
                             len(self._csv_paths_in_this_directory) + i + 1)

        self.__clean_existing_files()

        # No .csv files
        self.assertEqual(len(ExecutionElementMetricHelper.
                             _ExecutionElementMetricHelper__get_csv_files_in_directory(self._dir_path)), 0)

    def test_get_execution_elements_result_paths(self):
        os.mkdir(self._child_directory)
        os.mkdir(self._child_directory2)
        os.mkdir(self._child_directory3)

        # no files
        self.assertEqual(len(ExecutionElementMetricHelper.get_execution_elements_result_paths
                             (list([self._child_directory, self._child_directory2]))), 0)

        # add files in child_dir1
        for i in range(0, len(self._csv_paths_in_child_directory)):
            DataIO.write_csv(self._csv_paths_in_child_directory[i], self._csv_to_store)
            print(ExecutionElementMetricHelper.get_execution_elements_result_paths
                  (list([self._child_directory, self._child_directory2])))
            self.assertEqual(len(ExecutionElementMetricHelper.get_execution_elements_result_paths
                                 (list([self._child_directory, self._child_directory2]))), i + 1)

        # add files in child_dir2
        for i in range(0, len(self._csv_paths_in_child_directory2)):
            DataIO.write_csv(self._csv_paths_in_child_directory2[i], self._csv_to_store)
            self.assertEqual(len(ExecutionElementMetricHelper.get_execution_elements_result_paths
                                 (list([self._child_directory, self._child_directory2]))),
                             len(self._csv_paths_in_child_directory) + i + 1)

        # add files in child_dir3 -> child_dir3 is no parameter in function -> don't add it's csv paths
        for i in range(0, len(self._csv_paths_in_child_directory3)):
            DataIO.write_csv(self._csv_paths_in_child_directory3[i], self._csv_to_store)
            self.assertEqual(len(ExecutionElementMetricHelper.get_execution_elements_result_paths
                                 (list([self._child_directory, self._child_directory2]))),
                             len(self._csv_paths_in_child_directory) + len(self._csv_paths_in_child_directory2))

        # csv files in this directory (parent of the child directories) -> don't add it's csv paths
        for i in range(0, len(self._csv_paths_in_this_directory)):
            DataIO.write_csv(self._csv_paths_in_this_directory[i], self._csv_to_store)
            self.assertEqual(len(ExecutionElementMetricHelper.get_execution_elements_result_paths
                                 (list([self._child_directory, self._child_directory2]))),
                             len(self._csv_paths_in_child_directory) + len(self._csv_paths_in_child_directory2))

        self.__clean_existing_files()

    def test_convert_paths_into_subspace_identifier(self):
        # one element
        self.assertEqual(list(["first"]), ExecutionElementMetricHelper.
                         convert_paths_into_subspace_identifier(list([self._csv_paths_in_this_directory[0]])))

        # n elements
        self.assertEqual(list(["first", "second", "random_name"]), ExecutionElementMetricHelper.
                         convert_paths_into_subspace_identifier(list([self._csv_paths_in_this_directory[0],
                                                                      self._csv_paths_in_this_directory[1],
                                                                      self._csv_paths_in_this_directory[2]])))

        # empty
        self.assertEqual(list([""]), ExecutionElementMetricHelper.
                         convert_paths_into_subspace_identifier(list([""])))

        self.__clean_existing_files()

    def __clean_existing_files(self):
        if os.path.isdir(self._child_directory):
            shutil.rmtree(self._child_directory)

        if os.path.isdir(self._child_directory2):
            shutil.rmtree(self._child_directory2)

        if os.path.isdir(self._child_directory3):
            shutil.rmtree(self._child_directory3)

        for path in self._csv_paths_in_this_directory:
            if os.path.isfile(path):
                os.remove(path)

        if os.path.isfile(self._error_csv_path):
            os.remove(self._error_csv_path)


if __name__ == '__main__':
    unittest.main()
