from pathlib import Path
from typing import Optional

from django import forms
from django.core.files.uploadedfile import TemporaryUploadedFile

from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from experiments.models import Algorithm
from experiments.services.algorithm import (
    save_temp_algorithm,
    delete_temp_algorithm,
    convert_param_mapping_to_signature_dict,
)


class AdminAddAlgorithmForm(forms.ModelForm[Algorithm]):
    class Meta:
        model = Algorithm
        exclude = ["signature", "upload_date"]

    def clean_path(self) -> Optional[TemporaryUploadedFile]:
        cleaned_file: TemporaryUploadedFile = self.cleaned_data.get("path")  # type: ignore

        # current user is set in ModelAdmin of Algorithm
        temp_path: Path = save_temp_algorithm(self.current_user, cleaned_file)  # type: ignore
        error: Optional[str] = AlgorithmLoader.is_algorithm_valid(str(temp_path))
        if error is None:
            mapping = AlgorithmLoader.get_algorithm_parameters(str(temp_path))
            dikt = convert_param_mapping_to_signature_dict(mapping)
            self.instance.signature = dikt
        delete_temp_algorithm(temp_path)

        if error is not None:
            self.add_error("path", "This is not a valid algorithm: " + error)

        elif error is None:
            # No need to assign user, admin can decide to which user this algorithm belongs to
            return cleaned_file

        return None


class AdminChangeAlgorithmForm(forms.ModelForm[Algorithm]):
    class Meta:
        model = Algorithm
        exclude = ["path"]
