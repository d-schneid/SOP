from django import forms

from experiments.models import Algorithm, Dataset, Execution


class AlgorithmUploadForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        fields = ("display_name", "description", "group", "path")
        widgets = {
            "display_name": forms.TextInput(
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
        fields = ("display_name", "description", "path_original")
        widgets = {
            "display_name": forms.TextInput(
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
    class Meta:
        model = Execution
        fields = ("algorithm_parameters", "subspaces_min", "subspaces_max", "subspace_amount")
