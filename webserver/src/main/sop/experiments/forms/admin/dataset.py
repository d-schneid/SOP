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

        # save dataset temporarily
        temp_file_path: str = save_dataset(dataset)
        assert os.path.isfile(temp_file_path)

        try:
            dataset_valid = DatasetInfo.is_dataset_valid(temp_file_path)
        except UnicodeError as e:
            os.remove(temp_file_path)
            self.add_error("path_original", "Unicode error in selected dataset: " + e.reason)
            assert not os.path.isfile(temp_file_path)
            return None

        # check the dataset
        if not dataset_valid:
            os.remove(temp_file_path)
            self.add_error("path_original", "Selected dataset is not a valid csv-file.")
            assert not os.path.isfile(temp_file_path)
            return None

        dataset_path: str = dataset.name
        # and add data to the input (no datapoints / dimensions)
        self.cleaned_data.update({"is_cleaned": False,
                                  "path_cleaned__name": generate_path_dataset_cleaned(dataset_path)})
        # TODO: testen

        os.remove(temp_file_path)
        assert not os.path.isfile(temp_file_path)

        return self.cleaned_data


class AdminChangeDatasetForm(forms.ModelForm[Dataset]):
    class Meta:
        model = Dataset
        exclude = ["path_original", "path_cleaned"]
