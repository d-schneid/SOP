import shutil
import uuid
from typing import Final
from django.core.files.uploadedfile import UploadedFile

from authentication.models import User
from sop import settings

import os

DATASET_ROOT_DIR: Final = settings.MEDIA_ROOT / "datasets"


def save_dataset(file: UploadedFile, user: User) -> str:
    temp_dir = os.path.join(DATASET_ROOT_DIR, "temp", "user_" + str(user.pk))
    temp_file_path = os.path.join(temp_dir, str(uuid.uuid1()))

    assert not os.path.isfile(temp_file_path)

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # save contents of uploaded file into temp file
    with open(temp_file_path, "wb") as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)

    return temp_file_path


def check_if_file_is_csv(path: str) -> bool:
    return True
    # TODO -Finn (ist etwas mehr kompplex, muss ich mir selber basteln)


# TODO: Konsistende Umbenennung: user_id --> user.pk
def generate_path_dataset_uncleaned_and_move_dataset(temp_path: str, user_id: int, dataset_id: int) -> str:
    final_path: str = os.path.join(DATASET_ROOT_DIR, "user_" + str(user_id),
                                   "dataset_" + str(dataset_id) + "_uncleaned.csv")
    os.rename(temp_path, final_path)  # atomic operation
    return final_path


def generate_path_dataset_cleaned(user_id: int, dataset_id: int) -> str:
    return os.path.join(DATASET_ROOT_DIR, "user_" + str(user_id),
                                   "dataset_" + str(dataset_id) + "_cleaned.csv")
