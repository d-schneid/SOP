import numpy as np

from pyod.models.base import BaseDetector


class DebugAlgorithm(BaseDetector):

    def __init__(self, algorithm_result: int = 1):
        """
        :param algorithm_result: The result that will be outputted
        by calling decision_function()
        """
        self._algorithm_result: int = algorithm_result
        self.decision_scores_ = None

    def decision_function(self, X: np.ndarray):
        return np.repeat(self._algorithm_result, X.shape[0])

    def fit(self, X, y=None):
        self.decision_scores_ = np.repeat(self._algorithm_result, X.shape[0])

    def fit_predict(self, X, y=None):
        raise NotImplementedError

    def predict(self, X, return_confidence=False):
        raise NotImplementedError

    def predict_proba(self, X, method='linear', return_confidence=False):
        raise NotImplementedError

    def predict_confidence(self, X):
        raise NotImplementedError

    def _predict_rank(self, X, normalized=False):
        raise NotImplementedError

    def fit_predict_score(self, X, y, scoring='roc_auc_score'):
        raise NotImplementedError

    def _set_n_classes(self, y):
        raise NotImplementedError

    def _process_decision_scores(self):
        raise NotImplementedError

    def _get_param_names(self):
        raise NotImplementedError

    def get_params(self, deep=True):
        raise NotImplementedError

    def set_params(self, **params):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError
