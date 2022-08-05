from typing import Dict

from backend.JsonSerializable import JsonSerializable


class ParameterizedAlgorithm(JsonSerializable, object):
    """
    Used to describe one algorithm that is used in an execution.
    Saves all the important information about this algorithm.
    """

    def __init__(self, path: str, hyper_parameter: dict, display_name: str):
        """
        :param path: The absolute path where the algorithm is located.
        :param hyper_parameter: The hyperparameter of the algorithm with the selected values. Each parameter gets
         his own dictionary entry.
        :param display_name: The name of the algorithm that is shown to the user.
        """
        self._path: str = path
        self._hyper_parameter: dict = hyper_parameter
        self._display_name: str = display_name
        self._directory_name_in_execution: str = ""

    def to_json(self) -> Dict[str, object]:
        return {'display_name': self._display_name,
                'directory_name': self._directory_name_in_execution,
                'hyper_parameter': self._hyper_parameter}

    @property
    def path(self) -> str:
        """
        :return: The absolute path where the algorithm is located.
        """
        return self._path

    @property
    def hyper_parameter(self) -> dict[str, object]:
        """
        :return: The hyperparameter of the algorithm with the selected values. Each parameter
         gets his own dictionary entry.
        """
        return self._hyper_parameter

    @property
    def display_name(self) -> str:
        """
        :return: The name of the algorithm that is shown to the user.
        """
        return self._display_name

    @property
    def directory_name_in_execution(self) -> str:
        """
        :return: The name of the folder where the execution results for all ExecutionElements that computed there
        result with this algorithm are stored.
        """
        return self._directory_name_in_execution

    @directory_name_in_execution.setter
    def directory_name_in_execution(self, directory_name_in_execution: str) -> None:
        """
        :param directory_name_in_execution: The name of the folder where the execution results for all ExecutionElements
         that computed there result with this algorithm are stored.
        :return: None
        """
        self._directory_name_in_execution = directory_name_in_execution
