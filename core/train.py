import time
import warnings
import pickle
from flask import Blueprint, request, render_template, session
from model import gatherer
from model.preprocessing import Formatter, Extractor
from model.detection import Detector
from view import evaluation_metrics

#warnings.filterwarnings("ignore")

bp = Blueprint('train', __name__, url_prefix='/train')

@bp.route('/dataset')
def dataset():
    dataset_types = ['flows', 'aggregated flows']

    preprocessing = ['normal', 'standard scaler',
                     'minmax scaler', 'maxabs scaler',
                     'robust scaler', 'quantile transformer',
                     'normalizer']

    return render_template('train/dataset.html', dataset_types=dataset_types,
                           preprocessing=preprocessing)

@bp.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        session['path'] = '/home/flmoro/bsi16/research_project/codes/dataset/csv/'
        session['file'] = 'flows_w60_s800_cf.csv'
        session['aggregated'] = False
        session['preprocessing'] = int(request.form['preprocessing'])
        session['sample'] = int(request.form['sample'])
        session['test_size'] = int(request.form['test_size'])/100
        session['folds'] = int(request.form['folds'])


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

        features_size = 6
        features_start = 9

        if int(request.form['dataset_type']) == 1:
            features = ['source ports', 'destination ports'] + features
            features.append('flows')

            session['file'] = 'flows_w60_s800_af_l100.csv'
            session['aggregated'] = True

            features_size = 9
            features_start = 7

        if session['preprocessing'] in [1, 3, 4]:
            algorithms.remove('multinomial naive bayes')

        return render_template('train/config.html', algorithms=algorithms,
                               features=features, features_size=features_size,
                               features_start=features_start)


@bp.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        flows = gatherer.open_csv(session['path'], session['file'],
                                  session['sample'],
                                  True)[0]

        ft = Formatter(flows)
        header, flows = ft.format_flows(training_model=True)

        ex = Extractor()

        choice_features = [int(item) for item in
                           request.form.getlist('features')]

        header_features, features = ex.extract_features(header, flows,
                                                        choice_features)
        labels = ex.extract_labels(flows)

        features = ex.transform(features, session['preprocessing'])

        dataset = ex.train_test_split(features, labels, session['test_size'])

        dt = Detector()

        choice_algorithms = [int(item) for item in
                             request.form.getlist('algorithms')]
        num_clf = dt.choose_classifiers(choice_algorithms)

        information = []
        for idx in range(num_clf):
            dt.tuning_hyperparameters(session['folds'], idx)

            pred_parm, date, dur = dt.execute_classifiers(
                dataset[0], dataset[1], dataset[2], idx)

            metrics = evaluation_metrics(dataset[3], pred_parm[0], pred_parm[1],
                                         [date, dt.methods[idx], dur],
                                          session['path'] + "test.csv", idx)

            information.extend([[dt.methods[idx], date, dur, metrics[3],
                                 metrics[4], metrics[5], metrics[6],
                                 ex.methods, pred_parm[1]]])

            pickle.dump(dt, open('../objects/dt', 'wb'))
            pickle.dump(ex, open('../objects/ex', 'wb'))
            session['choice_features'] = choice_features

            text_info = ['date', 'duration', 'accuracy',
                         'precision', 'recall', 'f1-score',
                         'preprocessing method', 'hyperparameters']

        return render_template('train/results.html', information=information,
                               text_info=text_info)
