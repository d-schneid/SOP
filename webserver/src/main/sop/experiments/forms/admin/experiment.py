from typing import Optional, Any

from django import forms

from experiments.models import Experiment, Dataset
from experiments.models.managers import AlgorithmQuerySet

from authentication.models import User


class AdminAddExperimentForm(forms.ModelForm[Experiment]):
    class Meta:
        model = Experiment
        fields = ["display_name", "user", "dataset", "algorithms"]

    def clean(self) -> Optional[dict[str, Any]]:
        cleaned_user: Optional[User] = self.cleaned_data.get("user")
        cleaned_dataset: Optional[Dataset] = self.cleaned_data.get("dataset")
        cleaned_algorithms: Optional[AlgorithmQuerySet] = self.cleaned_data.get("algorithms")

        if not cleaned_dataset is None:
            if not cleaned_dataset.is_cleaned:
                self.add_error("dataset", "Selected dataset is not cleaned. "
                                          "Please select a cleaned dataset.")
            if not cleaned_dataset.user is None and not cleaned_user is None:
                if cleaned_dataset.user.id != cleaned_user.id:
                    self.add_error("dataset", "Selected user does not have access "
                                              "to this dataset. "
                                              "Please select an accessible dataset.")

        if cleaned_algorithms is None or cleaned_user is None:
            return self.cleaned_data

        for algorithm in cleaned_algorithms:
            if not algorithm.user is None:
                if algorithm.user.id != cleaned_user.id:
                    self.add_error("algorithms", "Selected user does not have access "
                                                 "to the selected algorithm "
                                                 f"{algorithm.display_name}.")
                    break

        return self.cleaned_data
