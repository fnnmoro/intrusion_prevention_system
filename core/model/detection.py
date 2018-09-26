import time
import numpy as np
from datetime import datetime
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import (SGDClassifier, PassiveAggressiveClassifier,
                                  Perceptron)
from sklearn.naive_bayes import BernoulliNB, GaussianNB, MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.model_selection import GridSearchCV
from .tools import processing_time
from view import checkpoint


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
                       "algorithm": ["ball_tree", "kd_tree", "brute"],
                       "leaf_size": [10, 20, 30]},

                      {"kernel": ["rbf"],
                       "C": [0.01, 0.1, 1.0, 10.0, 100.0],
                       "gamma": [0.0001, 0.001, 0.01, 0.1, 1.0]},

                      {"loss": ["hinge", "log", "modified_huber",
                                "squared_hinge", "perceptron"],
                       "penalty": ["l1", "l2", "elasticnet"],
                       "alpha": [0.0001, 0.001, 0.01, 0.1],
                       "fit_intercept": [True, False],
                       "max_iter": [5, 50, 500, 1000]},

                      {"C": [0.01, 0.1, 1.0, 10.0, 100.0],
                       "fit_intercept": [True, False],
                       "max_iter": [5, 50, 500, 1000],
                       "loss": ["hinge"]},

                      {"penalty": [None, "l1", "l2", "elasticnet"],
                       "alpha": [0.0001, 0.001, 0.01, 0.1],
                       "fit_intercept": [True, False],
                       "max_iter": [5, 50, 500, 1000]},

                      {"hidden_layer_sizes": [(10,), (100,), (10, 10)],
                       "activation": ["identity",  "logistic", "tanh", "relu"],
                       "solver": ["adam", "lbfgs", "sgd"],
                       "alpha": [0.0001, 0.001, 0.01, 0.1],
                       "max_iter": [5, 50, 500, 1000]}]

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

    def execute_classifiers(self, training_features, test_features,
                            training_labels, idx, execute_model=False):

        start = time.time()
        date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

        if not execute_model:
            self.classifiers[idx].fit(training_features, training_labels)
        pred = self.classifiers[idx].predict(test_features)
        param = self.classifiers[idx].best_params_

        end = time.time()
        dur = processing_time(start, end, no_output=True)

        return pred, param, date, dur

    @staticmethod
    def find_patterns(features):
        pca = PCA(n_components=2)

        pattern = pca.fit_transform(features)

        return pattern

    def find_anomalies(self, features, pred):
        anomalies = []

        for idx, lbl in enumerate(pred):
            if lbl == 1:
                anomalies.append(features[idx])

        return anomalies