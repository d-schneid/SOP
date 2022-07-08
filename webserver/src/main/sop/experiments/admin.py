from pathlib import Path
from typing import Optional

from django.core.files.uploadedfile import TemporaryUploadedFile
from django import forms
from django.contrib import admin

from experiments.models import Algorithm, Dataset
from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from sop.settings import MEDIA_ROOT
from experiments.services import (
    save_temp_algorithm,
    delete_temp_algorithm,
    get_signature_of_algorithm,
)

ALGORITHM_ROOT_DIR = MEDIA_ROOT / "algorithms"


admin.site.register(Dataset)


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