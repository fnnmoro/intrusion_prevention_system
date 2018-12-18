import pickle
import warnings
from tempfile import mkdtemp
from shutil import rmtree
from flask import Blueprint, request, render_template, session
from model import gatherer
from model.preprocessing import Formatter, Extractor
from model.detection import Detector
from view import evaluation_metrics
from core import csv_path


#warnings.filterwarnings("ignore")

bp = Blueprint('train', __name__, url_prefix='/train')

ex = Extractor()
dt = Detector()
files = ['flows_w60_s800_cf.csv', 'flows_w60_s800_af_l100.csv']

@bp.route('/dataset')
def dataset():
    dataset_types = ['IP flows', 'aggregated IP flows']

    return render_template('train/dataset.html', dataset_types=dataset_types,
                           preprocessing=ex.methods)

@bp.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        features_index = 7
        session['dataset_type'] = int(request.form['dataset_type'])
        session['sample'] = int(request.form['sample'])
        session['test_size'] = int(request.form['test_size']) / 100
        session['folds'] = int(request.form['folds'])

        if int(request.form['dataset_type']) == 0:
            ex.choose_features(0)
            features_index = 9

        ex.choose_preprocessing(int(request.form['preprocessing']))

        return render_template('train/config.html',
                               algorithms=dt.methods,
                               features=ex.features,
                               features_index=features_index)


@bp.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        flows = gatherer.open_csv(csv_path,
                                  files[session['dataset_type']],
                                  session['sample'],
                                  True)[0]

        ft = Formatter(flows)
        header, flows = ft.format_flows(training_model=True)

        choice_features = [int(item) for item in
                           request.form.getlist('features')]

        header_features, features = ex.extract_features(header, flows,
                                                        choice_features)

        labels = ex.extract_labels(flows)

        dataset = ex.train_test_split(features, labels, session['test_size'])

        choice_algorithms = [int(item) for item in
                             request.form.getlist('algorithms')]
        num_clf = dt.choose_classifiers(choice_algorithms)

        information = []
        temp_dir = mkdtemp()
        for idx in range(num_clf):
            dt.tuning_hyperparameters(session['folds'],
                                      idx,
                                      ex.preprocessing,
                                      temp_dir)

            param, train_date, train_dur = dt.training_classifiers(
                dataset[0], dataset[2], idx)

            pred, test_date, test_dur = dt.execute_classifiers(
                dataset[1], idx)

            metrics = evaluation_metrics(dataset[3], param, pred,
                                         [train_date, test_date, train_dur,
                                          test_dur, dt.methods[idx]],
                                          csv_path + "test.csv", idx)

            information.extend([[dt.methods[idx], train_date, test_date,
                                 train_dur, test_dur, metrics[5], metrics[6],
                                 metrics[7], metrics[8],
                                 ex.methods, param]])

            pickle.dump(dt, open('../objects/dt', 'wb'))
            pickle.dump(ex, open('../objects/ex', 'wb'))
            session['choice_features'] = choice_features

            text_info = ['train date', 'test date',
                         'train duration', 'test duration',
                         'accuracy', 'precision', 'recall', 'f1-score',
                         'preprocessing method', 'hyperparameters']
        rmtree(temp_dir)

        return render_template('train/results.html',
                               information=information,
                               text_info=text_info)
