import pickle
from datetime import datetime
from tempfile import mkdtemp
from shutil import rmtree
from flask import (request, render_template, session, Blueprint)
from path import paths
from model.detection import Detector
from model.gatherer import open_csv
from model.preprocess import Extractor, Formatter, Preprocessor
from model.tools import evaluation_metrics
from model.walker import get_files


ex = Extractor()
dt = Detector()
flows = None

bp = Blueprint('train', __name__, url_prefix='/train')

@bp.route('/load')
def load():
    files = get_files(f'{paths["saves"]}')

    return render_template('train/load.html', files=files)


@bp.route('/dataset')
def datasets():
    return render_template('train/datasets.html',
                           datasets=get_files(f'{paths["csv"]}datasets/'),
                           preprocesses=Preprocessor.methods.keys())

@bp.route('/classifiers', methods=['GET', 'POST'])
def classifiers():
    if request.method == 'POST':
        global flows

        header, flows = open_csv(f'{paths["csv"]}datasets/',
                                 request.form['dataset'],
                                 int(request.form['sample']))

        for entry in flows:
            Formatter.convert_features(entry, True)

        change_features_name = False
        if 'flw' in header:
            change_features_name = True
            setattr(ex, 'features_idx', 6)

        session['test_set_size'] = int(request.form['test_set_size'])/100
        session['k-folds'] = int(request.form['k-folds'])
        session['preprocess'] = request.form['preprocess']

        return render_template('train/classifiers.html',
                               classifiers=list(getattr(dt,
                                                        'classifiers').keys()),
                               change_features_name=change_features_name)


@bp.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        text = ['classifier', 'train date', 'test date',
                'train duration', 'test duration',
                'accuracy', 'precision', 'recall', 'f1-score',
                'tue negative', 'false positive',
                'false negative', 'true positive',
                'preprocess', 'hyperparameters']

        if request.referrer.split('/')[-1] == 'classifiers':
            setattr(ex, 'selected_features', [int(idx) for idx in
                                              request.form
                                              .getlist('features_name')])

            features, labels = ex.extract_features(flows)

            dataset = ex.train_test_split(features, labels,
                                          session['test_set_size'])

            info = list()
            tmp_dir = mkdtemp()
            for clf in request.form.getlist('classifiers'):
                dt.tuning_hyperparameters(clf,
                                          Preprocessor.methods
                                          [session['preprocess']],
                                          session['k-folds'],
                                          tmp_dir)

                param, train_date, train_dur = dt.train_classifier(clf,
                                                                   dataset[0],
                                                                   dataset[2])

                pred, test_date, test_dur = dt.execute_classifier(clf,
                                                                  dataset[1])

                results = ([clf, train_date, test_date, train_dur, test_dur]
                            + evaluation_metrics(dataset[3], pred)
                            + [session['preprocess'], param])
                info.append(results)

            rmtree(tmp_dir)
            pickle.dump(ex, open('obj/ex', 'wb'))
            pickle.dump(dt, open('obj/dt', 'wb'))
            pickle.dump([ex, dt, info],
                        open(f'saves/obj_'
                             f'{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                             'wb'))
        else:
            obj = pickle.load(open(f'saves/{request.form["file"]}', 'rb'))
            pickle.dump(obj[0], open('obj/ex', 'wb'))
            pickle.dump(obj[1], open('obj/dt', 'wb'))
            info = obj[2]

        return render_template('train/results.html',
                               text=text, info=info)
