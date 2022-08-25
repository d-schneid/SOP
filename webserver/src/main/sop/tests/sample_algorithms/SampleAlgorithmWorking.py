import numpy as np
import pyod.models.base


class SampleAlgorithmWorking(pyod.models.base.BaseDetector):
    def __init__(self, contamination=0.1):
        pass

    def fit(self, X, y=None):
        pass

    def decision_function(self, X):
        return np.zeros(X.shape[0])