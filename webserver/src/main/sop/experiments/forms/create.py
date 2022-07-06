from django import forms

from experiments.models import Algorithm


class AlgorithmUploadForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        fields = ("name", "description", "group", "path")
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control",
                       "placeholder": "algorithm name"}
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
    pass


class ExperimentCreateForm(forms.ModelForm):
    pass


class ExecutionCreateForm(forms.ModelForm):
    pass
