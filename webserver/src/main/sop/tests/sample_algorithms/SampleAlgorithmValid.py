from pyod.models.base import BaseDetector


class SampleAlgorithmValid(BaseDetector):
    def fit(self, X, y=None):
        pass

    def decision_function(self, X):
        pass

    def __init__(self, contamination=0.1):
        pass
