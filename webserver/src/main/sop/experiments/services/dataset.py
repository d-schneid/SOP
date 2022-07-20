import shutil
from typing import Final
from sop import settings

import os

DATASET_ROOT_DIR: Final = settings.MEDIA_ROOT / "datasets"


def check_if_file_is_csv(path: str) -> bool:
    return True
    # TODO -Finn (ist etwas mehr kompplex, muss ich mir selber basteln)


def generate_path_dataset_uncleaned_and_move_dataset(temp_path: str, user_id: int, dataset_id: int) -> str:
    final_path: str = os.path.join(DATASET_ROOT_DIR, "user_" + str(user_id),
                                   "dataset_" + str(dataset_id)  + "_uncleaned")
    shutil.move(temp_path, final_path)
    return final_path


def generate_path_dataset_cleaned(user_id: int, dataset_id: int) -> str:
    return os.path.join(DATASET_ROOT_DIR, "user_" + str(user_id),
                                   "dataset_" + str(dataset_id) + "_cleaned")
