from pyod.models.base import BaseDetector
from pyod.models.lunar import LUNAR
from sklearn.preprocessing import MinMaxScaler, StandardScaler


class LUNARWrapper(BaseDetector):

    def __init__(self, model_type="WEIGHT", n_neighbours=5, negative_sampling="MIXED",
                 val_size=0.1, scaler="minmaxscaler", epsilon=0.1, proportion=1.0,
                 n_epochs=200, lr=0.001, wd=0.1, verbose=0):

        if scaler not in ["minmaxscaler", "standardscaler", None]:
            raise ValueError(
                f"Scaler '{scaler}' is not a valid scaler. "
                "Valid scalers are 'minmaxscaler', 'standardscaler', or 'None'."
            )

        self.scaler = None
        if scaler == "minmaxscaler":
            self.scaler = MinMaxScaler()
        elif scaler == "standardscaler":
            self.scaler = StandardScaler()

        self.detector = LUNAR(model_type=model_type,
                              n_neighbours=n_neighbours,
                              negative_sampling=negative_sampling,
                              val_size=val_size,
                              scaler=self.scaler,
                              epsilon=epsilon,
                              proportion=proportion,
                              n_epochs=n_epochs,
                              lr=lr,
                              wd=wd,
                              verbose=verbose)

        self.decision_scores_ = None

    def fit(self, X, y=None):
        self.detector.fit(X, y)
        self.decision_scores_ = self.detector.decision_scores_

    def decision_function(self, X):
        # We do not need this for our purposes.
        pass
