import os
import unittest

import numpy as np

from backend.DataIO import DataIO
from backend.metric.MetricSubspaceOutlierAmount import MetricSubspaceOutlierAmount


class IntegrationTest_MetricSubspaceOutlierAmount(unittest.TestCase):
    _algorithm_directory_paths: list[str] = list([
        "./test/integration_tests/backend/metric/executionResultForTesting_DO_NOT_DELETE/algorithmResult1",
        "./test/integration_tests/backend/metric/executionResultForTesting_DO_NOT_DELETE/algorithmResult2",
        "./test/integration_tests/backend/metric/executionResultForTesting_DO_NOT_DELETE/algorithmResult3",
        "./test/integration_tests/backend/metric/executionResultForTesting_DO_NOT_DELETE/algorithmResult_empty"
    ])

    _metric_result_path1: str = \
        "./test/integration_tests/backend/metric/internal_tests_subspace_outlier_amount_metric_result1.csv"
    _metric_result_to_compare1: str = \
        "./test/integration_tests/backend/metric/subspace_outlier_amount_metric_result1_to_compare.csv"
    _wrong_metric_path: str = "I don't end with .csv :("

    def setUp(self) -> None:
        self.__clean_up_files()

        self._metric = MetricSubspaceOutlierAmount()

    def test_compute_metric(self):
        # compute metric of execution example folder
        self._metric.compute_metric(self._metric_result_path1, self._algorithm_directory_paths)
        np.testing.assert_array_equal(
            DataIO.read_uncleaned_csv(self._metric_result_path1, has_header=None),
            DataIO.read_uncleaned_csv(self._metric_result_to_compare1, has_header=None)
        )
        # clean up
        self.__clean_up_files()

    def test_wrong_metric_path(self):
        # Path doesn't end with .csv
        with self.assertRaises(AssertionError) as context:
            self._metric.compute_metric(self._wrong_metric_path, self._algorithm_directory_paths)
        # clean up
        self.__clean_up_files()

    def __clean_up_files(self):
        pass
        #if os.path.isfile(self._metric_result_path1):
            #os.remove(self._metric_result_path1)


if __name__ == '__main__':
    unittest.main()
