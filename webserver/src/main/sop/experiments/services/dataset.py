import os
import uuid
from typing import Final

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler
from backend.task.cleaning import DatasetCleaning
from experiments.callback import DatasetCallbacks
from experiments.models import Dataset

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


def schedule_backend(dataset: Dataset) -> None:

    # set and save the missing datafield entry for the cleaned csv file
    # name is the path relative to the media root dir --> use name, not path
    cleaned_path = generate_path_dataset_cleaned(dataset.path_original.name)
    dataset.path_cleaned.name = cleaned_path
    dataset.save()

    # create DatasetCleaning object
    dataset_cleaning: DatasetCleaning = DatasetCleaning(
        user_id=dataset.user.pk,
        task_id=dataset.pk,
        task_progress_callback=DatasetCallbacks.cleaning_callback,
        uncleaned_dataset_path=dataset.path_original.path,
        cleaned_dataset_path=cleaned_path,
        cleaning_steps=None,  # can be changed later on
    )

    # TODO: DO NOT do this here. Move it to AppConfig or whatever
    if UserRoundRobinScheduler._instance is None:
        UserRoundRobinScheduler()

    # start the cleaning
    dataset_cleaning.schedule()
