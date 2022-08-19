import os
import unittest

import numpy as np

from backend.metric.MetricDataPointsAreOutliers import MetricDataPointsAreOutliers
from backend.DataIO import DataIO


class IntegrationTest_MetricDataPointsAreOutlier(unittest.TestCase):
    _algorithm_directory_paths: list[str] = list([
        "./test/integration_tests/backend/metric" +
        "/executionResultForTesting_DO_NOT_DELETE/algorithmResult1",
        "./test/integration_tests/backend/metric" +
        "/executionResultForTesting_DO_NOT_DELETE/algorithmResult2",
        "./test/integration_tests/backend/metric" +
        "/executionResultForTesting_DO_NOT_DELETE/algorithmResult3",
        "./test/integration_tests/backend/metric" +
        "/executionResultForTesting_DO_NOT_DELETE/algorithmResult_empty"
    ])

    _metric_result_path1: str = \
        "./test/integration_tests/backend/metric" + \
        "/data_points_are_outlier_metric_result1.csv"
    _metric_result_to_compare1: str = \
        "./test/integration_tests/backend/metric" + \
        "/data_points_are_outlier_metric_result1_to_compare.csv"
    _metric_result_path2: str = \
        "./test/integration_tests/backend/metric" + \
        "/data_points_are_outlier_metric_result2.csv"
    _metric_result_to_compare2: str = \
        "./test/integration_tests/backend/metric" + \
        "/data_points_are_outlier_metric_result2_to_compare.csv"

    _wrong_metric_path: str = "I don't end with .csv :("

    _metric_default_indices: list[int] = list([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                               11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    _metric_other_indices: list[int] = list([3, 15415, -142, 12, 45, 8, 51, 999,
                                             -124, 5, 10, 11, 12, 13, 14, 15, 16,
                                             17, 18, 19, 192143])
    _metric_not_enough_indices: list[int] = list([42])

    def setUp(self) -> None:
        self.__clean_up_files()

        self._metric = MetricDataPointsAreOutliers(self._metric_default_indices)
        self._other_indices_metric = \
            MetricDataPointsAreOutliers(self._metric_other_indices)
        self._not_enough_indices_metric = \
            MetricDataPointsAreOutliers(self._metric_not_enough_indices)

        for algorithm_path in self._algorithm_directory_paths:
            self.assertTrue(os.path.isdir(algorithm_path))

    def test_compute_metric(self):
        # compute metric of execution example folder
        self._metric.compute_metric(self._metric_result_path1,
                                    self._algorithm_directory_paths)
        np.testing.assert_array_equal(
            DataIO.read_uncleaned_csv(self._metric_result_path1, has_header=None),
            DataIO.read_uncleaned_csv(self._metric_result_to_compare1, has_header=None)
        )
        # clean up
        self.__clean_up_files()

    def test_other_indices(self):
        # compute metric of execution example folder
        self._other_indices_metric.compute_metric(self._metric_result_path2,
                                                  self._algorithm_directory_paths)
        np.testing.assert_array_equal(
            DataIO.read_uncleaned_csv(self._metric_result_path2, has_header=None),
            DataIO.read_uncleaned_csv(self._metric_result_to_compare2, has_header=None)
        )
        # clean up
        self.__clean_up_files()

    def test_not_enough_indices(self):
        # compute metric of execution example folder
        self._other_indices_metric.compute_metric(self._metric_result_path1,
                                                  self._algorithm_directory_paths)

        # Indices amount doesn't match with data points amount -> AssertionError
        with self.assertRaises(AssertionError):
            self._not_enough_indices_metric. \
                compute_metric(self._metric_result_path1,
                               self._algorithm_directory_paths)

        # clean up
        self.__clean_up_files()

    def test_wrong_metric_path(self):
        # Path doesn't end with .csv
        with self.assertRaises(AssertionError):
            self._metric.compute_metric(self._wrong_metric_path,
                                        self._algorithm_directory_paths)
        # clean up
        self.__clean_up_files()

    def __clean_up_files(self):
        if os.path.isfile(self._metric_result_path1):
            os.remove(self._metric_result_path1)
        if os.path.isfile(self._metric_result_path2):
            os.remove(self._metric_result_path2)


if __name__ == '__main__':
    unittest.main()
