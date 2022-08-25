import os
import unittest

from backend.task.TaskHelper import TaskHelper
from backend.task.cleaning.DatasetCleaning import DatasetCleaning
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.subspace.RandomizedSubspaceGeneration import \
    RandomizedSubspaceGeneration as rsg
from backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution as usd
from experiments.models import Execution


class SystemTest_CleaningAndExecuting(unittest.TestCase):
    # for Cleaning and Execution #######################################################

    _cleaned_dataset_path: str = "./test/system_tests/backend/task/" \
                                 "cleaning_and_execution/" \
                                 "cleaned_dataset_for_execution.csv"

    _user_id: int = 214
    _task_id: int = 1553
    # Cleaning setup ###################################################################

    _uncleaned_dataset_path: str = "./test/datasets/canada_climate_uncleaned.csv"

    # Execution setup ##################################################################

    _result_path: str = "./test/system_tests/backend/task/" \
                        "execution/basic_tests/execution_folder_system_test1"
    _zipped_result_path: str = _result_path + ".zip"
    _details_path: str = os.path.join(_result_path, 'details.json')

    # subspace generation
    _subspace_size_min: int = 1
    _subspace_size_max: int = 5
    _subspace_amount = 4
    _subspace_seed = 42
    _data_dimensions_count: int = 26
    _subspace_generation: rsg = rsg(usd(_subspace_size_min, _subspace_size_max),
                                    _data_dimensions_count, _subspace_amount,
                                    _subspace_seed)

    # parameterized algorithms
    _algorithm_result: int = 42
    _hyper_parameter: dict = {'algorithm_result': _algorithm_result}
    _display_names: list[str] = ["display_name", "display_name",
                                 "different_display_name", "display_name"]
    _directory_names_in_execution: list[str] = ["display_name", "display_name (1)",
                                                "different_display_name",
                                                "display_name (2)"]

    _path: str = "./test/algorithms/DebugAlgorithm.py"
    _root_dir: str = "./test/"
    _algorithms: list[ParameterizedAlgorithm] = \
        list([ParameterizedAlgorithm(_path, _hyper_parameter, _display_names[0]),
              ParameterizedAlgorithm(_path, _hyper_parameter, _display_names[1]),
              ParameterizedAlgorithm(_path, _hyper_parameter, _display_names[2]),
              ParameterizedAlgorithm(_path, _hyper_parameter, _display_names[3])])

    _running_path = _result_path + ".I_am_running"
    _final_zip_path = _result_path + ".zip"

    def setUp(self) -> None:
        # create DatasetCleaning
        self._dc: DatasetCleaning = \
            DatasetCleaning(self._user_id, self._task_id,
                            self.__cleaning_task__progress_callback,
                            "no_uncleaned_dataset",
                            self._cleaned_dataset_path, None)

        # create Execution
        self._ex: Execution = Execution(self._user_id, self._task_id,
                                        self.__execution_task_progress_callback,
                                        self._cleaned_dataset_path,
                                        self._result_path, self._subspace_generation,
                                        self._algorithms,
                                        self.__metric_callback, 29221,
                                        self._final_zip_path,
                                        zip_running_path=self._zipped_result_path)

    def test_cleaning_and_execution(self):
        self.assertEqual(True, False)  # add assertion here

    # callbacks ########################################################################
    def __cleaning_task__progress_callback(self):
        pass

    def __execution_task_progress_callback(self):
        pass

    def __metric_callback(self):
        pass


if __name__ == '__main__':
    unittest.main()
