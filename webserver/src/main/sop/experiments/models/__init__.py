# These imports are needed for django to find the respective models in this
# module. We import the models by their real name so we can import them from
# experiments.models directly

from experiments.models.algorithm import AlgorithmModel
from experiments.models.dataset import DatasetModel
from experiments.models.execution import ExecutionModel
from experiments.models.experiment import ExperimentModel
