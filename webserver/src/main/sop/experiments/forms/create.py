from django import forms

from experiments.models import Algorithm, Dataset, Execution, Experiment


class AlgorithmUploadForm(forms.ModelForm[Algorithm]):
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


class DatasetUploadForm(forms.ModelForm[Dataset]):
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


class ExperimentCreateForm(forms.ModelForm[Experiment]):
    class Meta:
        model = Experiment
        fields = ["display_name", "dataset", ]
        widgets = {
            "display_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Experiment name"}
            ),
            "dataset": forms.Select(attrs={"class": "form-control"}),
        }


class ExecutionCreateForm(forms.ModelForm[Execution]):
    class Meta:
        model = Execution
        fields = (
            "subspaces_min",
            "subspaces_max",
            "subspace_amount",
            "subspace_generation_seed",
        )
        widgets = {
            "subspaces_min": forms.NumberInput(attrs={"placeholder": "minimum", "class": "form-control"}),
            "subspaces_max": forms.NumberInput(attrs={"placeholder": "maximum", "class": "form-control"}),
            "subspace_amount": forms.NumberInput(attrs={"placeholder": "amount", "class": "form-control"}),
            "subspace_generation_seed": forms.NumberInput(
                attrs={"placeholder": "random", "class": "form-control"}
            )
        }
