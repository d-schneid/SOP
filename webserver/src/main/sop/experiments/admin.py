import os
import shutil
from pathlib import Path
from typing import Optional

from django.core.files.uploadedfile import UploadedFile, TemporaryUploadedFile
from django import forms
from django.contrib import admin

from experiments.models import Algorithm, Dataset
from authentication.models import User
from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from sop.settings import MEDIA_ROOT

ALGORITHM_ROOT_DIR = MEDIA_ROOT / "algorithms"


admin.site.register(Dataset)


def save_temp_algorithm(user: User, file: UploadedFile):
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


def get_signature_of_algorithm(path: str) -> str:
    algorithm_parameters = AlgorithmLoader.get_algorithm_parameters(path)
    keys_values = algorithm_parameters.items()
    string_dict = {key: str(value) for key, value in keys_values}
    return ",".join(string_dict.values())


class AlgorithmAddForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        exclude = ["signature"]

    def clean(self):
        cleaned_data = self.cleaned_data
        file: TemporaryUploadedFile = cleaned_data.get('path')

        temp_path: Path = save_temp_algorithm(self.current_user, file)
        AlgorithmLoader.set_algorithm_root_dir(str(ALGORITHM_ROOT_DIR))
        AlgorithmLoader.ensure_root_dir_in_path()
        error: Optional[str] = AlgorithmLoader.is_algorithm_valid(str(temp_path))
        if error is None:
            self.instance.signature = get_signature_of_algorithm(str(temp_path))
        delete_temp_algorithm(temp_path)

        if error is not None:
            self.add_error("path", "This is not a valid algorithm")

        elif error is None:
            # No need to assign user, admin can decide to which user this algorithm belongs to
            return cleaned_data


@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    form = AlgorithmAddForm
    list_display = ['name', 'group', 'description', "user"]
    readonly_fields = ['upload_date']
    raw_id_fields = ["user"]
    list_filter = ["name"]
    search_fields = ["group", "name"]

    # override to get current user in form
    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        form.current_user = request.user
        return form