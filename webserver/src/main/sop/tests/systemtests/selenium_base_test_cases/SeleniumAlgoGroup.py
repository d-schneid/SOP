from enum import Enum


class SeleniumAlgoGroup(Enum):
    PROBABILISTIC: str = "Probabilistic"
    LINEAR_MODEL: str = "Linear Model"
    PROXIMITY_BASED: str = "Proximity Based"
    OUTLIER_ENSEMBLES: str = "Outlier Ensembles"
    NEURONAL_NETWORKS: str = "Neural Networks"
    COMBINATION: str = "Combination"
    GRAPH_BASED: str = "Graph Based"
    OTHER: str = "Other"
