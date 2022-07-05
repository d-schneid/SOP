# These imports are needed for django to find the respective models in this
# module. We import the models by their real name so we can import them from
# experiments.models directly

from experiments.models.algorithm import Algorithm
from experiments.models.dataset import Dataset
from experiments.models.execution import Execution
from experiments.models.experiment import Experiment
