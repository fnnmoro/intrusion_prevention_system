from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from model.tools import process_time_log


class Detector:
    """Detects anomalous flows using supervised machine learning models.

    Attributes
    ----------
    self.classifiers: dict
        Supervised machine learning algorithms with a set of parameters to be
        searched."""

    def __init__(self):
        self.classifiers = {
            'dt': {'name': 'Decision Tree',
                   'obj': DecisionTreeClassifier(),
                   'param': {'criterion': ['gini', 'entropy'],
                             'splitter': ['best', 'random'],
                             'max_depth': [3, 9, 15, 21],
                             'min_samples_split': [2, 5, 10],
                             'min_samples_leaf': [2, 5, 10],
                             'max_features': [None, 'sqrt']}},

            'gnb': {'name': 'Gaussian Naive Bayes',
                    'obj': GaussianNB(),
                    'param': {'var_smoothing': [0.00001, 0.01, 0.1, 1.0]}},

            'knn': {'name': 'K-Nearest Neighbors',
                    'obj': KNeighborsClassifier(),
                    'param': {'n_neighbors': [5, 10, 15],
                              'weights': ['uniform', 'distance'],
                              'algorithm': ['ball_tree', 'kd_tree'],
                              'leaf_size': [10, 20, 30]}},

            'mlp': {'name': 'Multi-Layer Perceptron',
                    'obj': MLPClassifier(),
                    'param': {'hidden_layer_sizes': [(10,), (15, 10),
                                                     (20, 15, 10)],
                              'activation': ['identity', 'logistic',
                                             'tanh', 'relu'],
                              'solver': ['adam', 'lbfgs', 'sgd'],
                              'alpha': [0.0001, 0.001, 0.01, 0.1],
                              'max_iter': [50, 100, 200, 500]}},

            'rf': {'name': 'Random Forest',
                   'obj': RandomForestClassifier(),
                   'param': {'n_estimators': [5, 10, 15],
                             'criterion': ['gini', 'entropy'],
                             'max_depth': [3, 9, 15, 21],
                             'min_samples_split': [2, 5, 10],
                             'min_samples_leaf': [2, 5, 10],
                             'max_features': [None, 'sqrt']}},

            'svm': {'name': 'Support Vector Machine',
                    'obj': SVC(),
                    'param': {'kernel': ['rbf'],
                              'C': [0.1, 1.0, 10.0],
                              'gamma': [0.001, 0.01, 0.1],
                              'cache_size': [5000.0]}}}

    def tuning_hyperparameters(self, clf, preprocess, kfolds, tmp_dir):
        """Exhaustive search over specified parameters values for an machine
        learning algorithm.

        Parameters
        ----------
        clf: str
            Machine learning classifier key.
        preprocess: obj
            Preprocess method.
        kfolds: int
            Number of k folds.
        tmp_dir: str
            Absoulute path of a temporary directory to cache each transformer
            after calling fit. It avoids computing the fit transformers many
            times in a case of grid search"""

        if preprocess:
            # avoids data leakage by ensuring that the same samples are used
            # to train the transformers and predictors.
            # chains multiple estimators into one in a fixed sequence of steps.
            self.classifiers[clf]['obj'] = Pipeline(
                [('preprocess', preprocess), self.classifiers[clf]['obj']],
                memory=tmp_dir)

            # necessary for doing grid searches
            for key in list(self.classifiers[clf]['param'].keys()):
                self.classifiers[clf]['param'][f'classifier__{key}'] = \
                self.classifiers[clf]['param'].pop(key)

        self.classifiers[clf]['obj'] = \
        GridSearchCV(self.classifiers[clf]['obj'],
                     self.classifiers[clf]['param'],
                     cv=kfolds)

    @process_time_log
    def train_classifier(self, clf, training_features, training_labels):
        """Trains the machine learning algorithm.

        Parameters
        ----------
        clf: str
            Machine learning classifier key.
        training_features: list
            Features to training the algorithm.
        training_labels: list
            Correct features labels to training the algorithm.

        Returns
        -------
        param
            Best parameters found by grid search."""

        self.classifiers[clf]['obj'].fit(training_features, training_labels)
        param = self.classifiers[clf]['obj'].best_params_

        return param

    @process_time_log
    def execute_classifier(self, clf, test_features):
        """Executes the machine learning algorithm.

        Parameters
        ----------
        clf: str
            Machine learning classifier key.
        test_features: list
            Features to classify.

        Returns
        -------
        pred
            Prediction for each test entry."""

        pred = self.classifiers[clf]['obj'].predict(test_features)

        return pred

    def add_predictions(self, flows, pred):
        """Adds the predictions performed in real time into the evaluated
        flows.

        Parameters
        ----------
        flows: list
            IP flows exported by the network devices.
        pred: list
            Predictions done by the model.

        Returns
        -------
        flows
            IP flows with the predictions."""

        for idx, entry in enumerate(flows):
            entry[-1] = pred[idx]

        return flows
