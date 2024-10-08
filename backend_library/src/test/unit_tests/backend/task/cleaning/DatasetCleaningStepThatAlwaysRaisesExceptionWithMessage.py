from abc import ABC

from backend.AnnotatedDataset import AnnotatedDataset
from backend.task.cleaning.DatasetCleaningStep import DatasetCleaningStep


class DatasetCleaningStepThatAlwaysRaisesExceptionWithMessage(DatasetCleaningStep,
                                                              ABC):
    """
    Every cleaning_step of the cleaning_pipeline has to implement this abstract class.
    """

    def do_cleaning(self, dataset_to_clean: AnnotatedDataset) -> AnnotatedDataset:
        """
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        raise Exception("The error message is not empty")
