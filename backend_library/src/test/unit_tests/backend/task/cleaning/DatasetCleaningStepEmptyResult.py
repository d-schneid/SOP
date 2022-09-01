from abc import ABC

from backend.AnnotatedDataset import AnnotatedDataset
from backend.task.cleaning.DatasetCleaningStep import DatasetCleaningStep
from backend_library.resources.test.datasets.DatasetsForTesting import Datasets


class DatasetCleaningStepEmptyResult(DatasetCleaningStep, ABC):
    """
    Every cleaning_step of the cleaning_pipeline has to implement this abstract class.
    """

    def do_cleaning(self, dataset_to_clean: AnnotatedDataset) -> AnnotatedDataset:
        """
        :param dataset_to_clean: The dataset that will be cleaned in this cleaning_step.
        :return: The cleaned dataset.
        """
        return Datasets().empty_annotated_dataset
