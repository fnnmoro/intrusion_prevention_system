import pickle
from datetime import datetime
from shutil import rmtree
from tempfile import mkdtemp

from flask import (Blueprint, redirect, request,
                   render_template, session, url_for)
from sklearn.model_selection import train_test_split

from app import db
from app.paths import paths
from app.core import gatherer
from app.core.detection import Detector
from app.core.preprocess import Extractor, Formatter, preprocessing
from app.core.tools import evaluation_metrics, get_content
from app.forms.setting import LoadForm, DatasetForm
from app.models.dataset import Dataset


bp = Blueprint('setting', __name__)


@bp.route('/load')
def load():
    return render_template('setting/load.html',
                           files=get_content(f'{paths["models"]}')[1],
                           form=LoadForm())


@bp.route('/dataset', methods=['GET', 'POST'])
def dataset():
    form = DatasetForm()

    datasets_names = list()
    datasets = get_content(f'{paths["csv"]}datasets/')[1]
    for idx, dataset in enumerate(datasets):
        datasets_names.append([dataset,
                              ' '.join(dataset.split('.csv')[0].split('_'))])
    form.dataset.choices = datasets_names

    if request.method == 'POST' and form.validate_on_submit():
        details = form.dataset.data.split('_')
        d = Dataset(file=form.dataset.data,
                    window=details[1].split('w')[-1],
                    aggregation=details[2].split('a')[-1],
                    size=details[3].split('.csv')[0].split('s')[-1],
                    sample=form.sample.data,
                    split=form.split.data,
                    kfolds=form.kfolds.data)
        db.session.add(d)
        db.session.commit()

        return redirect(url_for('setting.classifier'))
    return render_template('setting/dataset.html',
                           form=form)


@bp.route('/classifier', methods=['GET', 'POST'])
def classifier():


    return render_template('setting/classifier.html',
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
