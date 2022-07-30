import os
import uuid
from typing import Final

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import FieldFile
from django.http import HttpResponse

from authentication.models import User

DATASET_ROOT_DIR: Final = settings.MEDIA_ROOT / "datasets"


def save_dataset(file: UploadedFile, user: User) -> str:
    temp_dir = DATASET_ROOT_DIR / "temp" / f"user_{user.pk}"
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


def get_download_response(file: FieldFile, download_name: str) -> HttpResponse:
    response = HttpResponse(file.read())
    response["Content-Type"] = "text/plain"
    response["Content-Disposition"] = f"attachment; filename={download_name}"
    return response
