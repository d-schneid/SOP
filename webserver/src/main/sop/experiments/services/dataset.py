import shutil
from typing import Final
from sop import settings

import os

DATASET_ROOT_DIR: Final = settings.MEDIA_ROOT / "datasets"


def check_if_file_is_csv(path: str) -> bool:
    return True
    # TODO -Finn (ist etwas mehr kompplex, muss ich mir selber basteln)


def save_dataset_finally_uncleaned(temp_path: str, identifier: str) -> str:
    final_path: str = os.path.join(DATASET_ROOT_DIR, "dataset_" + identifier + "_uncleaned")
    shutil.move(temp_path, final_path)
    return final_path


def path_dataset_finally_cleaned(identifier: str) -> str:
    final_path: str = os.path.join(DATASET_ROOT_DIR, "dataset_" + identifier + "_cleaned")
    return final_path
