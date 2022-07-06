from django import forms

from experiments.models import Algorithm


class UploadAlgorithmForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        fields = ('name', 'group', 'path')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'algorithm name'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'path': forms.FileInput(attrs={'accept': ".py"}),
        }
