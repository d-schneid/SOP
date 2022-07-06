from django import forms

from experiments.models import Algorithm


class AlgorithmEditForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        fields = ("name", "description", "group")
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control",
                       "placeholder": "algorithm name"}
            ),
            "group": forms.Select(attrs={"class": "form-control"}),
        }


class DatasetEditForm(forms.ModelForm):
    pass


class ExperimentEditForm(forms.ModelForm):
    pass


class ExecutionEditForm(forms.ModelForm):
    pass
