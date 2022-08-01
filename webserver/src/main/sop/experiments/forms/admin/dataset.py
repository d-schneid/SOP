import os
from typing import Optional, Any, Dict

from backend.DatasetInfo import DatasetInfo
from django import forms
from django.core.files.uploadedfile import TemporaryUploadedFile
from experiments.models import Dataset
from experiments.services.dataset import save_dataset, generate_path_dataset_cleaned


class AdminAddDatasetForm(forms.ModelForm[Dataset]):
    class Meta:
        model = Dataset
        exclude = ["datapoints_total",
                   "dimensions_total",
                   "path_cleaned",
                   "is_cleaned"]

    def clean(self) -> Optional[Dict[str, Any]]:
        dataset: Optional[TemporaryUploadedFile] = self.cleaned_data.get("path_original")

        if dataset is None:
            return self.cleaned_data

        dataset_path: str = dataset.name

        # save dataset temporarily
        temp_file: str = save_dataset(dataset)

        # check the dataset
        if not DatasetInfo.is_dataset_valid(temp_file):
            self.add_error("path_original", "The dataset is not a valid csv-file.")
            return None

        # and add data to the input (no datapoints / dimensions)
        self.cleaned_data.update({"is_cleaned": False,
                                  "path_cleaned__name": generate_path_dataset_cleaned(dataset_path)})
        # TODO: testen

        # delete dataset
        os.remove(temp_file)

        return self.cleaned_data


class AdminChangeDatasetForm(forms.ModelForm[Dataset]):
    class Meta:
        model = Dataset
        exclude = ["path_original", "path_cleaned"]

