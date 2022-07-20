from django import forms

from experiments.models import Algorithm, Dataset, Experiment, Execution


class AlgorithmEditForm(forms.ModelForm[Algorithm]):
    class Meta:
        model = Algorithm
        fields = ("display_name", "description", "group")
        widgets = {
            "display_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Algorithm name"}
            ),
            "group": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Algorithm Description"}
            ),
        }


class DatasetEditForm(forms.ModelForm[Dataset]):
    class Meta:
        model = Dataset
        fields = ("display_name", "description")
        widgets = {
            "display_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Dataset name"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Dataset Description"}
            ),
        }


class ExperimentEditForm(forms.ModelForm[Experiment]):
    class Meta:
        model = Experiment
        fields = ("display_name",)
        widgets = {
            "display_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Experiment name"}
            )
        }


class ExecutionEditForm(forms.ModelForm[Execution]):
    pass
