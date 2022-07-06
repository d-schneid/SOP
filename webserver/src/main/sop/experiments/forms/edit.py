from django import forms

from experiments.models import Algorithm


class AlgorithmEditForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        fields = ('name', 'description', 'group')


class DatasetEditForm(forms.ModelForm):
    pass


class ExperimentEditForm(forms.ModelForm):
    pass


class ExecutionEditForm(forms.ModelForm):
    pass
