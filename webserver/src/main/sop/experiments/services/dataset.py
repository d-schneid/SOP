import uuid
from typing import Final
from django.core.files.uploadedfile import UploadedFile

from authentication.models import User
from sop import settings

import os

DATASET_ROOT_DIR: Final = settings.MEDIA_ROOT / "datasets"


def save_dataset(file: UploadedFile) -> str:
    temp_dir = os.path.join(DATASET_ROOT_DIR, "temp")
    temp_file_path = os.path.join(temp_dir, str(uuid.uuid1()))

    assert not os.path.isfile(temp_file_path)

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # save contents of uploaded file into temp file
    with open(temp_file_path, "wb") as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)

    return temp_file_path


def generate_path_dataset_cleaned(uncleaned_path: str) -> str:
    (root, ext) = os.path.splitext(uncleaned_path)
    return root + "_cleaned" + ext
