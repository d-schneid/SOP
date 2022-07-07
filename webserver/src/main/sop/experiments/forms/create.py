from django import forms

from experiments.models import Algorithm, Dataset


class AlgorithmUploadForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        fields = ("name", "description", "group", "path")
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "algorithm name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "algorithm description",
                }
            ),
            "group": forms.Select(attrs={"class": "form-control"}),
            "path": forms.FileInput(attrs={"accept": ".py"}),
        }


class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ("name", "description", "path_original")
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Dataset name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Dataset description",
                }
            ),
            "path_original": forms.FileInput(attrs={"accept": ".csv"}),
        }


class ExperimentCreateForm(forms.ModelForm):
    pass


class ExecutionCreateForm(forms.ModelForm):
    pass
