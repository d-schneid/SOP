from django import forms

from experiments.models import Dataset


class AdminAddDatasetForm(forms.ModelForm[Dataset]):
    class Meta:
        model = Dataset
        exclude = ["datapoints_total",
                   "dimensions_total",
                   "path_cleaned",
                   "is_cleaned"]

class AdminChangeDatasetForm(forms.ModelForm[Dataset]):
    class Meta:
        model = Dataset
        exclude = ["path_original", "path_cleaned"]
