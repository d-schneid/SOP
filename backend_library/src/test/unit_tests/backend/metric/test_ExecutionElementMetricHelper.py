import os
import shutil
import unittest

import numpy as np

from backend.metric.ExecutionElementMetricHelper import ExecutionElementMetricHelper
from backend.DataIO import DataIO


class UnitTest_ExecutionElementMetricHelper(unittest.TestCase):
    _dir_path: str = os.path.join(os.path.join(os.path.join(
        os.path.join(os.getcwd(), "test"), "unit_tests"), "backend"), "metric")

    _csv_to_store: np.ndarray = np.asarray([[42]])

    _csv_paths_in_this_directory: list[str] \
        = list([os.path.join(_dir_path, "first.csv"),
                os.path.join(_dir_path, "second.csv"),
                os.path.join(_dir_path, "random_name.csv")])

    _child_directory: str = os.path.join(_dir_path, "child_directory")
    _csv_paths_in_child_directory: list[str] = list(
        [os.path.join(_child_directory, "first.csv"),
         os.path.join(_child_directory, "second.csv"),
         os.path.join(_child_directory, "random_name.csv")])

    _child_directory2: str = os.path.join(_dir_path, "child_directory2")
    _csv_paths_in_child_directory2: list[str] = list(
        [os.path.join(_child_directory2, "first.csv"),
         os.path.join(_child_directory2, "second.csv"),
         os.path.join(_child_directory2, "random_name.csv")])

    _child_directory3: str = os.path.join(_dir_path, "child_directory3")
    _csv_paths_in_child_directory3: list[str] = list(
        [os.path.join(_child_directory3, "first.csv"),
         os.path.join(_child_directory3, "second.csv"),
         os.path.join(_child_directory3, "random_name.csv")])

    _error_csv_path: str = os.path.join(_dir_path, "this_element_failed.csv.error")
    _error_metric_path: str = "./test/unit_tests/backend/metric" \
                              "/error_metric.csv.error"

    def setUp(self) -> None:
        self.__clean_existing_files()

    def test_get_csv_files_in_directory(self):
        # No .csv files
        self.assertEqual(len(ExecutionElementMetricHelper.
        _ExecutionElementMetricHelper__get_csv_files_in_directory(
            self._dir_path)), 0)

        # csv files in this directory
        for i in range(0, len(self._csv_paths_in_this_directory)):
            DataIO.write_csv(self._csv_paths_in_this_directory[i], self._csv_to_store)
            self.assertEqual(len(ExecutionElementMetricHelper.
            _ExecutionElementMetricHelper__get_csv_files_in_directory(
                self._dir_path)), i + 1)

        # ignore error files
        DataIO.write_csv(self._error_csv_path, self._csv_to_store)
        self.assertEqual(len(ExecutionElementMetricHelper.
        _ExecutionElementMetricHelper__get_csv_files_in_directory(
            self._dir_path)),
            len(self._csv_paths_in_this_directory))

        # Cleaning
        self.__clean_existing_files()

        # No .csv files
        self.assertEqual(len(ExecutionElementMetricHelper.
        _ExecutionElementMetricHelper__get_csv_files_in_directory(
            self._dir_path)), 0)

    def test_get_execution_elements_result_paths(self):
        os.mkdir(self._child_directory)
        os.mkdir(self._child_directory2)
        os.mkdir(self._child_directory3)

        # no files
        self.assertEqual(
            len(ExecutionElementMetricHelper.get_execution_elements_result_paths
                (list([self._child_directory, self._child_directory2]))), 0)

        # add files in child_dir1
        for i in range(0, len(self._csv_paths_in_child_directory)):
            DataIO.write_csv(self._csv_paths_in_child_directory[i], self._csv_to_store)
            print(ExecutionElementMetricHelper.get_execution_elements_result_paths
                  (list([self._child_directory, self._child_directory2])))
            self.assertEqual(
                len(ExecutionElementMetricHelper.get_execution_elements_result_paths
                    (list([self._child_directory, self._child_directory2]))), i + 1)

        # add files in child_dir2
        for i in range(0, len(self._csv_paths_in_child_directory2)):
            DataIO.write_csv(self._csv_paths_in_child_directory2[i], self._csv_to_store)
            self.assertEqual(
                len(ExecutionElementMetricHelper.get_execution_elements_result_paths
                    (list([self._child_directory, self._child_directory2]))),
                len(self._csv_paths_in_child_directory) + i + 1)

        # add files in child_dir3 -> child_dir3 is no parameter in function
        # -> don't add it's csv paths
        for i in range(0, len(self._csv_paths_in_child_directory3)):
            DataIO.write_csv(self._csv_paths_in_child_directory3[i], self._csv_to_store)
            self.assertEqual(
                len(ExecutionElementMetricHelper.get_execution_elements_result_paths
                    (list([self._child_directory, self._child_directory2]))),
                len(self._csv_paths_in_child_directory) + len(
                    self._csv_paths_in_child_directory2))

        # csv files in this directory (parent of the child directories)
        # -> don't add it's csv paths
        for i in range(0, len(self._csv_paths_in_this_directory)):
            DataIO.write_csv(self._csv_paths_in_this_directory[i], self._csv_to_store)
            self.assertEqual(
                len(ExecutionElementMetricHelper.get_execution_elements_result_paths
                    (list([self._child_directory, self._child_directory2]))),
                len(self._csv_paths_in_child_directory) + len(
                    self._csv_paths_in_child_directory2))

        self.__clean_existing_files()

    def test_convert_paths_into_subspace_identifier(self):
        # one element
        self.assertEqual(list(["first"]), ExecutionElementMetricHelper.
                         convert_paths_into_subspace_identifier(
            list([self._csv_paths_in_this_directory[0]])))

        # n elements
        self.assertEqual(list(["first", "second", "random_name"]),
                         ExecutionElementMetricHelper.
                         convert_paths_into_subspace_identifier(
                             list([self._csv_paths_in_this_directory[0],
                                   self._csv_paths_in_this_directory[1],
                                   self._csv_paths_in_this_directory[2]])))

        # empty
        self.assertEqual(list([""]), ExecutionElementMetricHelper.
                         convert_paths_into_subspace_identifier(list([""])))

        self.__clean_existing_files()

    def test_compute_data_point_outlier_count(self):
        _execution_element_outlier_result_dataset1: list[np.ndarray] = list([
            np.asarray([True, True, True, True, False, False, False, False]),
            np.asarray([True, True, False, False, False, False, False, False]),
            np.asarray([True, False, False, False, False, False, False, False]),
            np.asarray([False, False, False, False, False, False, False, False])])
        _expected_result1: np.ndarray[int] = np.asarray(list([3, 2, 1, 1, 0, 0, 0, 0]))

        np.testing.assert_array_equal(ExecutionElementMetricHelper.
        compute_data_point_outlier_count(
            _execution_element_outlier_result_dataset1),
            _expected_result1)

    def test_compute_subspace_outlier_amount(self):
        _execution_element_outlier_result_dataset1: dict[str, list[np.ndarray]] = {
            "subspace1": list([
                np.asarray([True, True, True, True, False, False, False, False]),
                np.asarray([True, True, False, False, False, False, False, False])]),
            "subspace2": list([
                np.asarray([True, False, False, False, False, False, False, False]),
                np.asarray([False, False, False, False, False, False, False, False])]),
            "AHHHH, everything is an outlier D:": list([
                np.asarray([True, True, True, True, True, True, True, True]),
                np.asarray([True, True, True, True, True, True, True, True])]),
            "Not even one outlier :)": list([
                np.asarray([False, False, False, False, False, False, False, False]),
                np.asarray([False, False, False, False, False, False, False, False])])
        }

        _expected_result1: np.ndarray[int] = np.asarray(
            list([4 + 2, 1 + 0, 8 + 8, 0 + 0]))

        np.testing.assert_array_equal(ExecutionElementMetricHelper.
        compute_subspace_outlier_amount(
            _execution_element_outlier_result_dataset1),
            _expected_result1)

    def test_write_empty_execution_error_message(self):
        self.assertFalse(os.path.isfile(self._error_metric_path))
        ExecutionElementMetricHelper.write_empty_execution_error_message(
            self._error_metric_path)

        self.assertTrue(os.path.isfile(self._error_metric_path))
        pass

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
        if os.path.isfile(self._error_metric_path):
            os.remove(self._error_metric_path)


class UnitTest_ExecutionElementMetricHelper_ComputeOutlierDataPoints(unittest.TestCase):
    _dir_path: str = os.path.join(os.path.join(os.path.join(
        os.path.join(os.getcwd(), "test"), "unit_test"), "backend"), "metric")

    _execution_element_result_wrong_path: str = \
        "I don't end with .csv so now I'm evil?!"

    # dataset 1
    _execution_element_result_path1: str = os.path.join(os.getcwd(), "result_path1.csv")
    _execution_element_result_dataset1: np.ndarray = \
        np.asarray([[0, 1], [1, 0], [2, 0], [3, 0], [4, 0], [5, 1], [6, 1]])

    # dataset 2
    _execution_element_result_path2: str = os.path.join(os.getcwd(), "result_path2.csv")
    _execution_element_result_dataset2: np.ndarray = \
        np.asarray([[0, 0], [1, 0.1], [2, 0.2], [3, 0.3], [4, 0.4],
                    [5, 0.5], [6, 0.6], [7, 0.7], [8, 0.8], [9, 0.9], [10, 0.99],
                    [10, 1]])

    # dataset 3
    _array_values: list[float] = list(range(0, 10000))
    _normalized_values: list[float] = list([])
    for val in _array_values:
        _normalized_values.append(val / 10000.0)
    _execution_element_result_path3: str = os.path.join(os.getcwd(), "result_path3.csv")

    # dataset 4
    _execution_element_result_path4: str = os.path.join(os.getcwd(), "result_path4.csv")
    _execution_element_result_dataset4: np.ndarray = \
        np.asarray([[0, 1], [1, 1], [2, 1], [3, 1]])

    def setUp(self) -> None:
        self.__clean_existing_files()

    def __clean_existing_files(self):
        if os.path.isfile(self._execution_element_result_path1):
            os.remove(self._execution_element_result_path1)

        if os.path.isfile(self._execution_element_result_path2):
            os.remove(self._execution_element_result_path2)

        if os.path.isfile(self._execution_element_result_path3):
            os.remove(self._execution_element_result_path3)

        if os.path.isfile(self._execution_element_result_path4):
            os.remove(self._execution_element_result_path4)

    def test_compute_outlier_data_points(self):
        # invalid path
        with self.assertRaises(AssertionError):
            ExecutionElementMetricHelper.compute_outlier_data_points(
                self._execution_element_result_wrong_path)

        # dataset 1 (only 1 or 0 -> yes/no answers)
        DataIO.write_csv(self._execution_element_result_path1,
                         self._execution_element_result_dataset1)
        execution_element_expected_result1: np.ndarray = \
            np.asarray([True, False, False, False, False, True, True])
        np.testing.assert_array_equal(execution_element_expected_result1,
                                      ExecutionElementMetricHelper.
                                      compute_outlier_data_points(
                                          self._execution_element_result_path1))

        # dataset 2 (answers range between 0 and 1).
        # Only last entry is beyond percentile -> only one Outlier
        DataIO.write_csv(self._execution_element_result_path2,
                         self._execution_element_result_dataset2)
        execution_element_expected_result2: np.ndarray = \
            np.asarray(
                [False, False, False, False, False, False, False, False, False, False,
                 False, True])
        np.testing.assert_array_equal(execution_element_expected_result2,
                                      ExecutionElementMetricHelper.
                                      compute_outlier_data_points(
                                          self._execution_element_result_path2))

        # dataset 3
        DataIO.write_csv(self._execution_element_result_path3,
                         np.asarray(self._normalized_values), True)

        _expected_result3_list: list[bool] = list([])
        for val in range(0,
                         9900):  # Because we use a 0.99 quantile and have 10000 entries
            _expected_result3_list.append(False)
        for val in range(0, 100):
            _expected_result3_list.append(True)
        _expected_result3: np.ndarray = np.asarray(_expected_result3_list)

        np.testing.assert_array_equal(_expected_result3,
                                      ExecutionElementMetricHelper.
                                      compute_outlier_data_points(
                                          self._execution_element_result_path3))

        # dataset 4: each value is one -> everything is an outlier
        DataIO.write_csv(self._execution_element_result_path4,
                         self._execution_element_result_dataset4, False)
        np.testing.assert_array_equal(np.asarray([True, True, True, True]),
                                      ExecutionElementMetricHelper.
                                      compute_outlier_data_points(
                                          self._execution_element_result_path4))

        # clean up
        self.__clean_existing_files()


if __name__ == '__main__':
    unittest.main()
