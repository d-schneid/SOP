import inspect
from typing import Dict, Type

from pyod.models.base import BaseDetector


class AlgorithmLoader:
    _root_dir: str = None

    @staticmethod
    def set_algorithm_root_dir(directory: str):
        AlgorithmLoader._root_dir = directory

    @staticmethod
    def ensure_root_dir_in_path():
        pass

    @staticmethod
    def get_algorithm_class(path: str) -> Type[BaseDetector]:
        pass

    @staticmethod
    def get_algorithm_object(path: str, parameters: Dict[str, object]) -> BaseDetector:
        pass

    @staticmethod
    def is_algorithm_valid(path: str) -> str:
        pass

    @staticmethod
    def get_algorithm_parameters(path: str) -> inspect.Signature.parameters:
        pass