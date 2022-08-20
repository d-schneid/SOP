# These imports are needed for django to find the respective models in this
# module. We import the models by their real name, so we can import them from
# experiments.models directly

from experiments.models.algorithm import Algorithm as Algorithm  # noqa: F401
from experiments.models.dataset import Dataset as Dataset  # noqa: F401
from experiments.models.execution import Execution as Execution  # noqa: F401
from experiments.models.experiment import Experiment as Experiment  # noqa: F401
