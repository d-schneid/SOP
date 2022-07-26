from typing import Optional, Any

from django import forms
from django.conf import settings

from experiments.models import Experiment, Dataset
from experiments.models.managers import AlgorithmQuerySet


class AdminAddExperimentForm(forms.ModelForm[Experiment]):
    class Meta:
        model = Experiment
        fields = "__all__"

    def clean(self) -> Optional[dict[str, Any]]:
        cleaned_user: settings.AUTH_USER_MODEL = self.cleaned_data.get("user")
        cleaned_dataset: Dataset = self.cleaned_data.get("dataset")
        cleaned_algorithms: AlgorithmQuerySet = self.cleaned_data.get("algorithms")

        if cleaned_dataset.user:
            if cleaned_dataset.user.id != cleaned_user.id:
                self.add_error("dataset", "Selected user does not have access "
                                          "to this dataset.")

        for algorithm in cleaned_algorithms:
            if algorithm.user:
                if algorithm.user.id != cleaned_user.id:
                    self.add_error("algorithms", "Selected user does not have access "
                                                 "to the selected algorithm "
                                                 f"{algorithm.display_name}.")
                    break

        if self.has_error("dataset") or self.has_error("algorithms"):
            return None

        return self.cleaned_data

