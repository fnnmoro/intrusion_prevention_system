import pickle
from datetime import datetime
from shutil import rmtree
from tempfile import mkdtemp

from flask import Blueprint, request, render_template, session
from sklearn.model_selection import train_test_split

from app.paths import paths
from app.core import gatherer
from app.core.detection import Detector
from app.core.preprocess import Extractor, Formatter, preprocessing
from app.core.tools import evaluation_metrics, get_content
from app.forms.setting import LoadForm, DatasetForm


flows = list()

bp = Blueprint('setting', __name__)


@bp.route('/load')
def load():
    return render_template('setting/load.html',
                           files=get_content(f'{paths["models"]}')[1],
                           form=LoadForm())


@bp.route('/dataset')
def dataset():
    form = DatasetForm()

    datasets_names = list()
    datasets = get_content(f'{paths["csv"]}datasets/')[1]
    for idx, dataset in enumerate(datasets):
        datasets_names.append([idx,
                              ' '.join(dataset.split('.csv')[0].split('_'))])
    form.dataset.choices = datasets_names

    preprocessing_names = list()
    for method in preprocessing:
        preprocessing_names.append([method, ' '.join(method.split('_'))])
    form.preprocessing.choices = preprocessing_names

    return render_template('setting/dataset.html',
                           form=form)


@bp.route('/classifiers', methods=['GET', 'POST'])
def classifiers():
    global flows
    if request.method == 'POST':
        header, flows = gatherer.open_csv(f'{paths["csv"]}datasets/',
                                          request.form['dataset'],
                                          int(request.form['sample']))

        for entry in flows:
            Formatter.convert_features(entry, True)

        extractor = Extractor(8, list())
        if 'flw' in header:
            setattr(extractor, 'start_index', 6)
        features_names = extractor.extract_features_names()

        session['start_index'] = getattr(extractor, 'start_index')
        session['test_size'] = int(request.form['test_size'])/100
        session['k-folds'] = int(request.form['k-folds'])
        session['preprocess_key'] = request.form['preprocess_key']

        return render_template('setting/classifiers.html',
                               classifiers=getattr(Detector(), 'classifiers'),
                               features_names=features_names)


@bp.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        if request.referrer.split('/')[-1] == 'classifiers':
            extractor = Extractor(session['start_index'],
                                  [int(idx) for idx in
                                  request.form.getlist('features_name')])

            features, labels = extractor.extract_features(flows)

            dataset = train_test_split(features, labels,
                                       test_size=session['test_size'],
                                       random_state=13,
                                       stratify=labels)

            preprocess = Preprocessor.methods[session['preprocess_key']]['obj']

            results = list()
            # creates an absolute path of a temporary directory
            tmp_dir = mkdtemp()
            detector = Detector()
            for clf in request.form.getlist('classifiers_keys'):
                detector.tuning_hyperparameters(clf,
                                                preprocess,
                                                session['k-folds'],
                                                tmp_dir)

                param, train_date, train_dur = detector.train_classifier(clf,
                                                                   dataset[0],
                                                                   dataset[2])

                pred, exec_date, exec_dur = detector.execute_classifier(clf,
                                                                  dataset[1])

                outcome = {'clf':
                              {'name': 'Classifier',
                               'result': [clf, getattr(detector,
                                               'classifiers')[clf]['name']]}}
                outcome.update(evaluation_metrics(dataset[3], pred))
                outcome.update({'tdt': {'name': 'Training date',
                                        'result': train_date},
                                'edt': {'name': 'Execution date',
                                        'result': exec_date},
                                'tdur': {'name': 'Training duration',
                                         'result': train_dur},
                                'edur': {'name': 'Execution duration',
                                         'result': exec_dur},
                                'param': {'name': 'Hyperparameters',
                                          'result': param}})
                results.append(outcome)
            rmtree(tmp_dir)
            session['obj_name'] = f'obj_{datetime.now().strftime("%Y%m%d%H%M%S")}'
            pickle.dump([extractor, detector, results],
                        open(f'{paths["models"]}{session["obj_name"]}', 'wb'))
        else:
            session['obj_name'] = f'{request.form["model"]}'
            obj = pickle.load(open(f'{paths["models"]}{session["obj_name"]}',
                                   'rb'))
            results=obj[2]

        return render_template('setting/results.html',
                               results=results)
