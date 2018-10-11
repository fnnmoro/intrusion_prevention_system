import time
import warnings
import pickle
from flask import Blueprint, request, render_template
from model import gatherer
from model.preprocessing import Formatter, Extractor
from model.detection import Detector
from view import evaluation_metrics

#warnings.filterwarnings("ignore")

bp = Blueprint('train', __name__, url_prefix='/train')

@bp.route('/config')
def config():
    algorithms = ['decision tree',
                  'random forest',
                  'bernoulli naive bayes',
                  'gaussian naive bayes',
                  'multinomial naive bayes',
                  'k-nearest neighbors',
                  'support vector machine',
                  'stochastic gradient descent',
                  'passive aggressive',
                  'perceptron',
                  'multi-layer perceptron']

    features = ['duration', 'packets', 'bytes', 'bits per second',
                'bits per packets', 'packtes per second']

    preprocessing = ['normal', 'standard scaler',
                     'minmax scaler', 'maxabs scaler',
                     'robust scaler', 'quantile transformer']

    return render_template('train/config.html', algorithms=algorithms,
                           features=features, preprocessing=preprocessing)


@bp.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        path = '/home/flmoro/research_project/dataset/csv/'
        file = 'flows_w60_s800_cf.csv'

        flows = gatherer.open_csv(path, file, int(request.form['sample']),
                                  True)[0]

        ft = Formatter(flows)
        header, flows = ft.format_flows(training_model=True)

        ex = Extractor()

        choice_features = [int(item) for item in
                           request.form.getlist('features')]
        header_features, features = ex.extract_features(header, flows,
                                                        choice_features)
        labels = ex.extract_labels(flows)

        features = ex.feature_scaling(features,
                                      int(request.form['preprocessing']))

        dataset = ex.train_test_split(features, labels,
                                      int(request.form['test_size'])/100)

        dt = Detector()

        choice_algorithms = [int(item) for item in
                             request.form.getlist('algorithms')]
        num_clf = dt.choose_classifiers(choice_algorithms)

        information = []
        for idx in range(num_clf):
            dt.tuning_hyperparameters(int(request.form['kfold']), idx)

            pred, param, date, dur = dt.execute_classifiers(
                dataset[0], dataset[1], dataset[2], idx)

            metrics = evaluation_metrics(dataset[3], pred, param,
                                         [date, dt.methods[idx], dur],
                                         path + "test.csv", idx)

            information.extend([[dt.methods[idx], date, dur, metrics[3],
                                 metrics[4], metrics[5], metrics[6],
                                 ex.methods[int(request.form['preprocessing'])],
                                 param]])

            pickle.dump(dt, open('../objects/dt', 'wb'))
            pickle.dump(ex, open('../objects/ex', 'wb'))
            pickle.dump([choice_features, int(request.form['preprocessing'])],
                        open('../objects/forms', 'wb'))

        return render_template('train/results.html', information=information)
