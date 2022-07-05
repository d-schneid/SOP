from django import forms
from experiments.models import Algorithm

class UploadAlgorithmForm(forms.ModelForm):

	class Meta:
		model = Algorithm
		fields = ('_name', '_group', '_path')
		widgets = {
			'_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'algorithm name'}),
			'_group': forms.Select(attrs={'class': 'form-control'}),
			'_path': forms.FileInput(attrs={'accept': ".py"}),
		}