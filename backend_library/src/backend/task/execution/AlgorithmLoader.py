import importlib
import inspect
import os.path
import pathlib
import sys
from types import ModuleType
from typing import Dict, Type, Optional

from pyod.models.base import BaseDetector


class AlgorithmLoader:
    """helper class for runtime-loading pyod BaseDetectors"""
    _root_dir: Optional[str] = None

    @staticmethod
    def set_algorithm_root_dir(directory: str) -> None:
        """
        Sets the root directory of the AlgorithmLoader.
        Should only be executed once
        :param directory: path of the root directory to be set.
        All algorithms to be loaded have to be in its subdirectories
        """
        if directory[-1] in ['/', '\\']:
            directory = directory[:-1]
        AlgorithmLoader._root_dir = directory

    @staticmethod
    def _ensure_root_dir_in_path() -> None:
        """adds the _root_dir to sys.path, if missing"""
        assert AlgorithmLoader._root_dir is not None, \
            "set_algorithm_root_dir has to be executed before"
        if AlgorithmLoader._root_dir not in sys.path:
            sys.path.append(AlgorithmLoader._root_dir)

    @staticmethod
    def get_algorithm_class(path: str) -> Type[BaseDetector]:
        """Retrieves the type object for the algorithm under the given path"""
        assert os.path.isfile(path), 'path is not an existing file'
        assert os.path.splitext(path)[1] == '.py', 'path must be a python file'
        class_name: str = os.path.splitext(os.path.basename(path))[0]
        lower_class_name = class_name.lower()
        AlgorithmLoader._ensure_root_dir_in_path()
        path_obj: pathlib.Path = pathlib.Path(path)
        assert path_obj.is_relative_to(AlgorithmLoader._root_dir), \
            'path must be contained in root dir'
        relative_location: path = path_obj.parent.relative_to(AlgorithmLoader._root_dir)
        import_path: tuple[str, ...] = relative_location.parts
        assert len(import_path) > 0, 'the file must not be directly in the root dir'
        module_name: str = f"{'.'.join(import_path)}.{class_name}"
        module: ModuleType = importlib.import_module(module_name)
        class_name: str = \
            next((x for x in dir(module) if x.lower() == lower_class_name), None)
        assert class_name is not None, 'file does not contain a class of the same name'
        requested_class = getattr(module, class_name)
        assert issubclass(requested_class, BaseDetector), \
            f"{class_name} is not a subclass of pyod.models.base.BaseDetector"
        return requested_class

    @staticmethod
    def get_algorithm_object(path: str, parameters: Dict[str, object]) -> BaseDetector:
        """instantiates an instance of the BaseDetector implementation
        under the given path with the given constructor parameters"""
        return AlgorithmLoader.get_algorithm_class(path)(**parameters)

    @staticmethod
    def is_algorithm_valid(path: str) -> Optional[str]:
        """verifies that under the given path a valid BaseDetector implementation exists
        :returns an error message or None if the algorithm is valid
        """
        try:
            AlgorithmLoader.get_algorithm_class(path)
        except Exception as ex:
            return str(ex)
        else:
            return None

    @staticmethod
    def get_algorithm_parameters(path: str) -> inspect.Signature.parameters:
        """reads the parameters of the constructor of the BaseDetector implementation
        under the given path, and if existing the default parameter value"""
        return inspect.signature(AlgorithmLoader.get_algorithm_class(path)).parameters
