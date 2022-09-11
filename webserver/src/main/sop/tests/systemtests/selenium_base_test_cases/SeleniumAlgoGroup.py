from enum import Enum


class SeleniumAlgoGropu(Enum):
    PROBABILISTIC: str = "Probabilistic"
    LINEAR_MODEL: str = "Linear Model"
    PROXIMITY_BASED: str = "Proximity Based"
    OUTLIER_ENSEMBLES: str = "Outlier Ensembles"
    NEURONAL_NETWORKS: str = "Neural Networks"
    COMBINATION: str = "Combination"
    OTHER: str = "Other"
