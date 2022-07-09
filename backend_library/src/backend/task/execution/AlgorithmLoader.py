import importlib
import inspect
import os.path
import pathlib
import sys
from types import ModuleType
from typing import Dict, Type, Optional

from pyod.models.base import BaseDetector


class AlgorithmLoader:
    _root_dir: str = None

    @staticmethod
    def set_algorithm_root_dir(directory: str):
        if directory[-1] in ['/', '\\']:
            directory = directory[:-1]
        AlgorithmLoader._root_dir = directory

    @staticmethod
    def ensure_root_dir_in_path():
        if AlgorithmLoader._root_dir not in sys.path:
            sys.path.append(AlgorithmLoader._root_dir)
        pass

    @staticmethod
    def get_algorithm_class(path: str) -> Type[BaseDetector]:
        assert os.path.isfile(path), 'path is not an existing file'
        assert os.path.splitext(path)[1] == '.py', 'path must be a python file'
        class_name: str = os.path.splitext(os.path.basename(path))[0]
        lower_class_name = class_name.lower()
        AlgorithmLoader.ensure_root_dir_in_path()
        path_obj: pathlib.Path = pathlib.Path(path)
        assert path_obj.is_relative_to(AlgorithmLoader._root_dir), 'path must be contained in root dir'
        import_path: tuple[str, ...] = path_obj.parent.relative_to(AlgorithmLoader._root_dir).parts
        assert len(import_path) > 0, 'the file must not be directly in the root dir'
        module: ModuleType = importlib.import_module(('.'.join(import_path)) + '.' + class_name)
        class_name: str = next((x for x in dir(module) if x.lower() == lower_class_name), None)
        assert class_name is not None, 'file does not contain a class of the same name'
        requested_class = getattr(module, class_name)
        assert issubclass(requested_class, BaseDetector), f"{class_name} is not a subclass of pyod.models.base.BaseDetector"
        return requested_class

    @staticmethod
    def get_algorithm_object(path: str, parameters: Dict[str, object]) -> BaseDetector:
        return AlgorithmLoader.get_algorithm_class(path)(**parameters)

    @staticmethod
    def is_algorithm_valid(path: str) -> Optional[str]:
        try:
            AlgorithmLoader.get_algorithm_class(path)
        except Exception as ex:
            return str(ex)
        else:
            return None

    @staticmethod
    def get_algorithm_parameters(path: str) -> inspect.Signature.parameters:
        return inspect.signature(AlgorithmLoader.get_algorithm_class(path)).parameters
