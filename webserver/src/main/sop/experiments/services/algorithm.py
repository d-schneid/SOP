import os
import shutil
from inspect import Parameter
from pathlib import Path
from types import MappingProxyType
from typing import Final, List

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from authentication.models import User
from backend.task.execution.AlgorithmLoader import AlgorithmLoader

ALGORITHM_ROOT_DIR: Final = settings.MEDIA_ROOT / "algorithms"


def save_temp_algorithm(user: User, file: UploadedFile) -> Path:
    temp_dir = ALGORITHM_ROOT_DIR / "temp" / f"{user.id}"
    temp_file_path = temp_dir / file.name

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # save contents of uploaded file into temp file
    with open(temp_file_path, "wb") as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)

    return temp_file_path


def delete_temp_algorithm(temp_file_path: Path):
    parent_folder = temp_file_path.parent
    assert temp_file_path.parent.parent == ALGORITHM_ROOT_DIR / "temp"

    if not os.path.isdir(temp_file_path.parent):
        return

    # remove temp file
    temp_file_path.unlink()

    # remove parent dir if it has no files in it (ignore directories in it, since
    # __pycache__ could have been created)
    if not any([os.path.isfile(file) for file in os.listdir(parent_folder)]):
        shutil.rmtree(parent_folder)


def convert_param_mapping_to_signature_dict(
    mapping: MappingProxyType[str, Parameter]
) -> dict[str, List[dict[str, object]]]:
    dikt = dict()
    for name, param in mapping.items():
        # we need to do this check, because the kwargs default parameter is a type,
        # and we can't handle that better
        dikt[name] = param.default if type(param.default) != type else None
    return dikt
