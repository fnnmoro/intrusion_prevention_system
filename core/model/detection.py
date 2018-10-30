from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import BernoulliNB, GaussianNB, MultinomialNB
from sklearn.linear_model import (SGDClassifier, PassiveAggressiveClassifier,
                                  Perceptron)
from .tools import processing_time_log


class Detector:
    """Detects anomalous flow using machine learning algorithms"""

    def __init__(self):
        """Initializes the main variables"""
        self.methods = ["decision tree",
                        "random forest",
                        "bernoulli naive bayes",
                        "gaussian naive bayes",
                        "multinomial naive bayes",
                        "k-nearest neighbors",
                        "support vector machine",
                        "stochastic gradient descent",
                        "passive aggressive",
                        "perceptron",
                        "multi-layer perceptron"]

        self.classifiers = [DecisionTreeClassifier(),
                            RandomForestClassifier(),
                            BernoulliNB(),
                            GaussianNB(),
                            MultinomialNB(),
                            KNeighborsClassifier(),
                            SVC(),
                            SGDClassifier(),
                            PassiveAggressiveClassifier(),
                            Perceptron(),
                            MLPClassifier()]

        self.param = [{"criterion": ["gini", "entropy"],
                       "splitter": ["best", "random"],
                       "max_depth": [3, 9, 15, 21],
                       "min_samples_split": [2, 5, 10],
                       "min_samples_leaf": [2, 5, 10],
                       "max_features": ["sqrt", None],},

                      {"n_estimators": [5, 10, 15],
                       "criterion": ["gini", "entropy"],
                       "max_depth": [3, 9, 15, 21],
                       "min_samples_split": [2, 5, 10],
                       "min_samples_leaf": [2, 5, 10],
                       "max_features": [None, "sqrt"]},

                      {"alpha": [0.001, 0.01, 0.1, 1.0],
                       "fit_prior": [True, False]},

                      {},

                      {"alpha": [0.001, 0.01, 0.1, 1.0],
                       "fit_prior": [True, False]},

                      {"n_neighbors": [5, 10, 15],
                       "weights": ["uniform", "distance"],
                       "algorithm": ["ball_tree", "kd_tree"],
                       "leaf_size": [10, 20, 30]},

                      {"kernel": ["rbf"],
                       "C": [0.01, 0.1, 1.0, 10.0, 100.0],
                       "gamma": [0.0001, 0.001, 0.01, 0.1, 1.0]},

                      {"loss": ["hinge", "log", "modified_huber",
                                "squared_hinge", "perceptron"],
                       "penalty": ["l1", "l2", "elasticnet"],
                       "alpha": [0.0001, 0.001, 0.01, 0.1],
                       "fit_intercept": [True, False],
                       "max_iter": [50, 100, 200, 500]},

                      {"C": [0.01, 0.1, 1.0, 10.0, 100.0],
                       "fit_intercept": [True, False],
                       "max_iter": [50, 100, 200, 500],
                       "loss": ["hinge"]},

                      {"penalty": [None, "l1", "l2", "elasticnet"],
                       "alpha": [0.0001, 0.001, 0.01, 0.1],
                       "fit_intercept": [True, False],
                       "max_iter": [50, 100, 200, 500]},

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

    def tuning_hyperparameters(self, n_splits, idx):
        self.classifiers[idx] = GridSearchCV(self.classifiers[idx],
                                             self.param[idx], cv=n_splits)

    @processing_time_log
    def execute_classifiers(self, training_features, test_features,
                            training_labels, idx, execute_model=False):
        if not execute_model:
            self.classifiers[idx].fit(training_features, training_labels)
        pred = self.classifiers[idx].predict(test_features)
        param = self.classifiers[idx].best_params_

        return pred, param

    def find_anomalies(self, flows, pred):
        anomalies = 0

        for idx, entry in enumerate(flows):
            entry[-1] = pred[idx]

            if pred[idx] == 1:
                anomalies += 1

        return flows, anomalies