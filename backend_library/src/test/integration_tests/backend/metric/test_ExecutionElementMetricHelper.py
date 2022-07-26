import os
import shutil
import unittest

import numpy as np

from backend.metric.ExecutionElementMetricHelper import ExecutionElementMetricHelper


class IntegrationTest_ExecutionElementMetricHelper(unittest.TestCase):
    _dir_path: str = os.path.join(os.path.join(os.path.join(
        os.path.join(os.getcwd(), "test"), "unit_tests"), "backend"), "metric")

    # dataset 1
    _execution_element_directory_path1: str = os.path.join(os.getcwd(), "algorithm_result_directory")
    _execution_element_result_dataset1: list[np.ndarray] = list([
        np.asarray([[0, 1], [1, 1], [2, 1], [3, 1], [4, 0], [5, 0], [6, 0], [7, 0]]),
        np.asarray([[0, 1], [1, 1], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0]]),
        np.asarray([[0, 1], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0]]),
        np.asarray([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0]])])
    _execution_element_result_dataset_path1: list[str] = list([
        os.path.join(os.getcwd(), "result1.csv"),
        os.path.join(os.getcwd(), "result2.csv"),
        os.path.join(os.getcwd(), "result3.csv"),
        os.path.join(os.getcwd(), "result4.csv")])

    def setUp(self) -> None:
        self.__clean_existing_files()

    def __clean_existing_files(self):
        if os.path.isdir(self._execution_element_directory_path1):
            shutil.rmtree(self._execution_element_directory_path1)


if __name__ == '__main__':
    unittest.main()
