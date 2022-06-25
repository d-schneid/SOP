import json
import string


class ParameterizedAlgorithm(object):

    def __init__(self, path: string, hyper_parameter: dict, display_name: string):
        self._path: string = path
        self._hyper_parameter: dict = hyper_parameter
        self._display_name: string = display_name
        self._directory_name_in_execution: string = ""

    def to_json(self) -> string:
        to_json_dict = {'display_name': self._display_name, 'hyper_parameter': self._hyper_parameter}
        json_string = json.dumps(to_json_dict)  # maybe set indent=4
        return json_string

    @property
    def path(self) -> string:
        return self._path

    @property
    def hyper_parameter(self) -> dict:
        return self._hyper_parameter

    @property
    def display_name(self) -> string:
        return self._display_name

    @property
    def directory_name_in_execution(self) -> string:
        return self._directory_name_in_execution

    @directory_name_in_execution.setter
    def directory_name_in_execution(self, directory_name_in_execution: string) -> None:
        self._directory_name_in_execution = directory_name_in_execution
