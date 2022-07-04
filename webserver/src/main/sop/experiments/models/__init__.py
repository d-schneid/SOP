# These imports are needed for django to find the respective models in this
# module. We import the models as "_XModel", so a user cannot do this:
#       from experiments.models import XModel
# but has to do it in the correct way:
#       from experiments.models.x import XModel

from experiments.models.algorithm import AlgorithmModel as _AlgorithmModel
from experiments.models.dataset import DatasetModel as _DatasetModel
from experiments.models.execution import ExecutionModel as _ExecutionModel
from experiments.models.experiment import ExperimentModel as _ExperimentModel
