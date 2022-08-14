import os
import uuid

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import FieldFile
from django.http import HttpResponse

from backend.task.cleaning.DatasetCleaning import DatasetCleaning
from experiments.callback import DatasetCallbacks
from experiments.models import Dataset


def save_dataset(file: UploadedFile) -> str:
    """
    Saves the given file that contains the dataset at a temporary location.
    @param file: A UploadedFile object containing the uploaded dataset.
    @return: The path to the temporary location as a string.
    """
    temp_dir = os.path.join(settings.DATASET_ROOT_DIR, "temp")
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
    """
    Generates the path for the cleaned csv of a dataset out of the uncleaned path.
    @param uncleaned_path: The path of the uncleaned csv.
    @return: The path of the cleaned csv as a string.
    """
    (root, ext) = os.path.splitext(uncleaned_path)
    return root + "_cleaned" + ext


def schedule_backend(dataset: Dataset) -> None:
    """
    Schedules a DatasetCleaning task in the backend.
    @param dataset: The dataset model for which a cleaning should be started.
    @return: None
    """

    # set and save the missing datafield entry for the cleaned csv file
    # name is the path relative to the media root dir --> use name, not path
    dataset.path_cleaned.name = generate_path_dataset_cleaned(
        dataset.path_original.name)
    dataset.save()

    # create DatasetCleaning object
    dataset_cleaning: DatasetCleaning = DatasetCleaning(
        user_id=dataset.user.pk,
        task_id=dataset.pk,
        task_progress_callback=DatasetCallbacks.cleaning_callback,
        uncleaned_dataset_path=dataset.path_original.path,
        cleaned_dataset_path=dataset.path_cleaned.path,
        cleaning_steps=None,  # can be changed later on
    )

    # start the cleaning
    dataset_cleaning.schedule()


def get_download_response(file: FieldFile, download_name: str) -> HttpResponse:
    """
    Generates a HttpResponse for a download with the content of a given FieldFile with a
    given name for the downloaded file.
    @param file: The file which should be downloaded.
    @param download_name: The default name of the downloaded file.
    @return: A HttpResponse with the download.
    """
    response = HttpResponse(file.read())
    response["Content-Type"] = "text/plain"
    response["Content-Disposition"] = f"attachment; filename={download_name}"
    return response
