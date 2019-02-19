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
    ''''Detects anomalous flow using machine learning algorithms'''

    def __init__(self):
        ''''Initializes the main variables'''

        self.classifiers = {
            'decision tree': [DecisionTreeClassifier(),
                              {'criterion': ['gini', 'entropy'],
                               'splitter': ['best', 'random'],
                               'max_depth': [3, 9, 15, 21],
                               'min_samples_split': [2, 5, 10],
                               'min_samples_leaf': [2, 5, 10],
                               'max_features': [None, 'sqrt']}],

            'gaussian naive bayes': [GaussianNB(),
                                     {'var_smoothing':
                                      [0.00001, 0.01, 0.1, 1.0]}],

            'k-nearest neighbors': [KNeighborsClassifier(),
                                    {'n_neighbors': [5, 10, 15],
                                     'weights': ['uniform', 'distance'],
                                     'algorithm': ['ball_tree', 'kd_tree'],
                                     'leaf_size': [10, 20, 30]}],

            'multi-layer perceptron': [MLPClassifier(),
                                       {'hidden_layer_sizes': [(10,), (15, 10),
                                                               (20, 15, 10)],
                                        'activation': ['identity', 'logistic',
                                                     'tanh', 'relu'],
                                        'solver': ['adam', 'lbfgs', 'sgd'],
                                        'alpha': [0.0001, 0.001, 0.01, 0.1],
                                        'max_iter': [50, 100, 200, 500]}],

            'random forest': [RandomForestClassifier(),
                              {'n_estimators': [5, 10, 15],
                               'criterion': ['gini', 'entropy'],
                               'max_depth': [3, 9, 15, 21],
                               'min_samples_split': [2, 5, 10],
                               'min_samples_leaf': [2, 5, 10],
                               'max_features': [None, 'sqrt']}],

            'support vector machine': [SVC(),
                                       {'kernel': ['rbf'],
                                        'C': [0.1, 1.0, 10.0],
                                        'gamma': [0.001, 0.01, 0.1],
                                        'cache_size': [5000.0]}]}

    def tuning_hyperparameters(self, clf, preprocess, n_splits, tmp_dir):
        if preprocess:
            # pipeline was used instead of make_pipe due the general step name
            self.classifiers[clf][0] = Pipeline([('preprocess', preprocess),
                                                 ('classifier',
                                                  self.classifiers[clf][0])],
                                                tmp_dir)

            for key in list(self.classifiers[clf][1].keys()):
                self.classifiers[clf][1][f'classifier__{key}'] = \
                    self.classifiers[clf][1].pop(key)

        self.classifiers[clf][0] = GridSearchCV(self.classifiers[clf][0],
                                                self.classifiers[clf][1],
                                                cv=n_splits)

    @process_time_log
    def train_classifier(self, clf, training_features, training_labels):

        self.classifiers[clf][0].fit(training_features, training_labels)
        param = self.classifiers[clf][0].best_params_

        return param

    @process_time_log
    def execute_classifier(self, clf, test_features):
        pred = self.classifiers[clf][0].predict(test_features)

        return pred

    def add_predictions(self, flows, pred):
        for idx, entry in enumerate(flows):
            entry[-1] = pred[idx]

        return flows
