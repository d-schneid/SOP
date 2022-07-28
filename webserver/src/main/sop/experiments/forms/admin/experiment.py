from typing import Optional, Dict

from django import forms

from experiments.models import Experiment, Dataset
from experiments.models.managers import AlgorithmQuerySet

from authentication.models import User


class AdminAddExperimentForm(forms.ModelForm[Experiment]):
    class Meta:
        model = Experiment
        fields = ["display_name", "user", "dataset", "algorithms"]

    def clean(self) -> Optional[Dict[str, object]]:
        cleaned_user: Optional[User] = self.cleaned_data.get("user")
        cleaned_dataset: Optional[Dataset] = self.cleaned_data.get("dataset")
        cleaned_algorithms: Optional[AlgorithmQuerySet] = self.cleaned_data.get("algorithms")

        if not (cleaned_dataset is None)\
                and not (cleaned_dataset.user is None)\
                and not (cleaned_user is None):
            if cleaned_dataset.user.id != cleaned_user.id:
                self.add_error("dataset", "Selected user does not have access "
                                          "to this dataset.")

        if not (cleaned_algorithms is None) and not (cleaned_user is None):
            for algorithm in cleaned_algorithms:
                if not (algorithm.user is None):
                    if algorithm.user.id != cleaned_user.id:
                        self.add_error("algorithms", "Selected user does not have access "
                                                     "to the selected algorithm "
                                                     f"{algorithm.display_name}.")
                        break

        return self.cleaned_data

