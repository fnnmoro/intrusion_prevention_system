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

    @staticmethod
    def define_parameters():
        dtr = {"criterion": ["gini", "entropy"],
               "splitter": ["best", "random"],
               "max_depth": [2, 5, 10, 20],
               "min_samples_split": [2, 5, 10],
               "min_samples_leaf": [1, 5, 10]}

        raf = {"n_estimators": [5, 10, 15],
               "criterion": ["gini", "entropy"],
               "max_features": ["auto", "log2", None],
               "max_depth": [2, 5, 10, 20],
               "min_samples_split": [2, 5, 10],
               "min_samples_leaf": [1, 5, 10],
               "bootstrap": [True, False]}

        bnb = {"alpha": [0.0001, 0.01, 0.1],
               "fit_prior": [True, False]}

        gnb = {}

        mnb = {"alpha": [0.0001, 0.01, 0.1],
               "fit_prior": [True, False]}

        knn = {"n_neighbors": [5, 10, 15],
               "weights": ["uniform", "distance"],
               "algorithm": ["ball_tree", "kd_tree", "brute"],
               "leaf_size": [1, 15, 30]}

        svm = [{"kernel": ["linear"],
                "C": [0.01, 0.1, 1.0, 10.0]},
               {"kernel": ["rbf"],
                "C": [0.01, 0.1, 1.0, 10.0],
                "gamma": [0.01, 0.1, 1.0, 10.0]}]

        sgd = {"loss": ["hinge", "modified_huber", "perceptron"],
               "penalty": ["l1", "l2", "elasticnet"],
               "max_iter": [int(np.ceil(10**6 / 60398)), 50, 100],
               "alpha": [0.0001, 0.01, 0.1],
               "learning_rate": ["constant", "optimal"],
               "eta0": [0.5, 1.0]}

        pag = {"C": [0.01, 0.1, 1.0, 10.0],
               "max_iter": [int(np.ceil(10 ** 6 / 60398)), 50, 100],
               "loss": ["hinge"]}

        ppn = {"penalty": ["l1", "l2", "elasticnet"]}

        mlp = {"hidden_layer_sizes": [(5, 2), (7, 5)],
               "activation": ["relu", "tanh", "logistic"],
               "solver": ["sgd", "lbfgs", "adam"],
               "alpha": [0.0001, 0.01, 0.1],
               "max_iter": [int(np.ceil(10**6 / 60398)), 50, 100],
               "learning_rate": ["constant", "invscaling", "adaptive"]}

        param = [dtr, raf, bnb, gnb, mnb, knn, svm, sgd, pag, ppn, mlp]

        return param

    def tuning_hyperparameters(self, param, cv):
        for i in range(len(self.classifiers)):
            self.classifiers[i] = GridSearchCV(self.classifiers[i],
                                               param[i],
                                               cv=cv,
                                               scoring="f1")

    def execute_classifiers(self, training_features, test_features,
                            training_labels, execute_model=False):
        pred = []
        param = []
        duration = []
        date = []

        idx = 0
        for clf in self.classifiers:
            start = time.time()
            date.append(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))

            if execute_model == False:
                clf.fit(training_features, training_labels)
            pred.append(clf.predict(test_features))
            param.append(clf.best_params_)

            end = time.time()
            duration.append(processing_time(start, end, no_output=True))

            checkpoint("classifier" + str(idx),
                       "/home/flmoro/research_project/log/checkpoint.csv")
            idx += 1

        return pred, param, date, duration

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