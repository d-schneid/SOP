import os
from typing import Optional, Any

from backend.DatasetInfo import DatasetInfo
from django import forms
from django.core.files.uploadedfile import TemporaryUploadedFile
from experiments.models.dataset import Dataset, CleaningState
from experiments.services.dataset import save_dataset, generate_path_dataset_cleaned


class AdminAddDatasetForm(forms.ModelForm[Dataset]):
    """
    The form that associates with the Dataset model and is used for the addition of
    Dataset model instances in the admin interface.
    """
    class Meta:
        model = Dataset
        exclude = [
            "datapoints_total",
            "dimensions_total",
            "path_cleaned",
            "status",
            "cleaning_progress",
        ]

    def clean(self) -> Optional[dict[str, Any]]:
        """
        Validates the dataset file of this AdminAddDatasetForm.
        If this dataset file is not valid, it shows an appropriate error for the
        respective field in this AdminAddDatasetForm on the respective add view in
        the admin interface.

        @return: The clean fields of this AdminAddDatasetForm if the dataset file is
        valid. Otherwise None.
        """
        dataset: Optional[TemporaryUploadedFile] = self.cleaned_data.get(
            "path_original")

        if dataset is None:
            return self.cleaned_data

        # save dataset temporarily
        temp_file_path: str = save_dataset(dataset)
        assert os.path.isfile(temp_file_path)

        try:
            dataset_valid = DatasetInfo.is_dataset_valid(temp_file_path)
        except UnicodeError as e:
            os.remove(temp_file_path)
            self.add_error("path_original",
                           f"Unicode error in selected dataset: {e.reason}")
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
        self.cleaned_data.update({"status": CleaningState.RUNNING.name,
                                  "path_cleaned__name":
                                      generate_path_dataset_cleaned(dataset_path)})

        os.remove(temp_file_path)
        assert not os.path.isfile(temp_file_path)

        return self.cleaned_data


class AdminChangeDatasetForm(forms.ModelForm[Dataset]):
    """
    The form that associates with the Dataset model and is used for the editing of
    Dataset model instances in the admin interface.
    """
    class Meta:
        model = Dataset
        exclude = ["path_original", "path_cleaned"]
