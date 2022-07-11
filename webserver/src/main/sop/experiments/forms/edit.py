from django import forms

from experiments.models import Algorithm, Dataset, Experiment


class AlgorithmEditForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        fields = ("display_name", "description", "group")
        widgets = {
            "display_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Algorithm name"}
            ),
            "group": forms.Select(attrs={"class": "form-control"}),
        }


class DatasetEditForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ("display_name", "description")
        widgets = {
            "display_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Dataset name"}
            )
        }


class ExperimentEditForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ("display_name",)
        widgets = {
            "display_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Experiment name"}
            )
        }


class ExecutionEditForm(forms.ModelForm):
    pass
