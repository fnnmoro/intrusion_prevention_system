from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from .tools import processing_time_log


class Detector:
    """Detects anomalous flow using machine learning algorithms"""

    def __init__(self):
        """Initializes the main variables"""
        self.methods = ["decision tree",
                        "random forest",
                        "gaussian naive bayes",
                        "k-nearest neighbors",
                        "support vector machine",
                        "multi-layer perceptron"]

        self.classifiers = [DecisionTreeClassifier(),
                            RandomForestClassifier(),
                            GaussianNB(),
                            KNeighborsClassifier(),
                            SVC(),
                            MLPClassifier()]

        self.param = [{"criterion": ["gini", "entropy"],
                       "splitter": ["best", "random"],
                       "max_depth": [3, 9, 15, 21],
                       "min_samples_split": [2, 5, 10],
                       "min_samples_leaf": [2, 5, 10],
                       "max_features": [None, "sqrt"]},

                      {"n_estimators": [5, 10, 15],
                       "criterion": ["gini", "entropy"],
                       "max_depth": [3, 9, 15, 21],
                       "min_samples_split": [2, 5, 10],
                       "min_samples_leaf": [2, 5, 10],
                       "max_features": [None, "sqrt"]},

                      {"var_smoothing": [0.000000001, 0.01, 0.1, 1.0]},

                      {"n_neighbors": [5, 10, 15],
                       "weights": ["uniform", "distance"],
                       "algorithm": ["ball_tree", "kd_tree"],
                       "leaf_size": [10, 20, 30]},

                       {"kernel": ["rbf"],
                       "C": [0.1, 1.0, 10.0],
                       "gamma": [0.001, 0.01, 0.1],
                       "cache_size": [5000.0]},

                      {"hidden_layer_sizes": [(10,), (15, 10), (20,15,10)],
                       "activation": ["identity",  "logistic", "tanh", "relu"],
                       "solver": ["adam", "lbfgs", "sgd"],
                       "alpha": [0.0001, 0.001, 0.01, 0.1],
                       "max_iter": [50, 100, 200, 500]}]

    def choose_classifiers(self, choices):
        tmp = [[],[],[]]

        for idx in choices:
            tmp[0].append(self.methods[idx])
            tmp[1].append(self.classifiers[idx])
            tmp[2].append(self.param[idx])

        self.methods = tmp[0]
        self.classifiers = tmp[1]
        self.param = tmp[2]

        num_clf = len(self.classifiers)

        return num_clf

    def tuning_hyperparameters(self, n_splits, idx, preprocessing, temp_dir):
        if preprocessing is not None:
            # pipeline was used instead of make_pipe due the general step name
            self.classifiers[idx] = Pipeline([('preprocessing',
                                               preprocessing),
                                              ('classifier',
                                               self.classifiers[idx])],
                                               temp_dir)

            for key in list(self.param[idx].keys()):
                self.param[idx][f'classifier__{key}'] = self.param[idx].pop(key)

        self.classifiers[idx] = GridSearchCV(self.classifiers[idx],
                                             self.param[idx],
                                             cv=n_splits)

    @processing_time_log
    def training_classifiers(self, training_features, training_labels, idx):

        self.classifiers[idx].fit(training_features, training_labels)
        param = self.classifiers[idx].best_params_

        return param

    @processing_time_log
    def execute_classifiers(self, test_features, idx):
        pred = self.classifiers[idx].predict(test_features)

        return pred

    def find_anomalies(self, flows, pred):
        anomalous_flows = []

        for idx, entry in enumerate(flows):
            if pred[idx] == 1:
                entry[-1] = pred[idx]
                anomalous_flows.append(entry)

        return anomalous_flows
