import unittest

from backend.metric.MetricDataPointsAreOutliers import MetricDataPointsAreOutliers


class IntegrationTest_MetricDataPointsAreOutlier(unittest.TestCase):

    _algorithm_directory_paths: list[str] = list([
        "./test/integration_tests/backend/metric/executionResultForTesting_DO_NOT_DELETE/algorithmResult1",
        "./test/integration_tests/backend/metric/executionResultForTesting_DO_NOT_DELETE/algorithmResult2",
        "./test/integration_tests/backend/metric/executionResultForTesting_DO_NOT_DELETE/algorithmResult3",
        "./test/integration_tests/backend/metric/executionResultForTesting_DO_NOT_DELETE/algorithmResult_empty"
    ])

    _metric_result_path: str = \
        "./test/integration_tests/backend/metric/integration_test_data_points_are_outlier_metric_result.csv"
    _wrong_metric_path: str = "I don't end with .csv :("

    def setUp(self) -> None:
        self._metric = MetricDataPointsAreOutliers()

    def test_compute_metric(self):
        self.assertEqual(True, False)  # add assertion here

    def test_wrong_metric_path(self):
        # Path doesn't end with .csv
        with self.assertRaises(AssertionError) as context:
            self._metric.compute_metric(self._wrong_metric_path, self._algorithm_directory_paths)


if __name__ == '__main__':
    unittest.main()
