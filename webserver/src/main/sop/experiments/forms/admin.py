from pathlib import Path
from typing import Optional

from django.core.files.uploadedfile import TemporaryUploadedFile
from django import forms

from experiments.models import Algorithm
from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from django.conf import settings
from experiments.services.algorithm import (
    save_temp_algorithm,
    delete_temp_algorithm,
    get_signature_of_algorithm,
)

ALGORITHM_ROOT_DIR = settings.MEDIA_ROOT / "algorithms"


class AdminAddAlgorithmForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        exclude = ["signature", "upload_date"]

    def clean_path(self):
        cleaned_file: TemporaryUploadedFile = self.cleaned_data.get("path")

        # current user is set in ModelAdmin of Algorithm
        temp_path: Path = save_temp_algorithm(self.current_user, cleaned_file)
        AlgorithmLoader.set_algorithm_root_dir(str(ALGORITHM_ROOT_DIR))
        AlgorithmLoader.ensure_root_dir_in_path()
        error: Optional[str] = AlgorithmLoader.is_algorithm_valid(str(temp_path))
        if error is None:
            self.instance.signature = get_signature_of_algorithm(str(temp_path))
        delete_temp_algorithm(temp_path)

        if error is not None:
            self.add_error("path", "This is not a valid algorithm: " + error)

        elif error is None:
            # No need to assign user, admin can decide to which user this algorithm belongs to
            return cleaned_file


class AdminChangeAlgorithmForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        exclude = ["path", "signature"]
