import copy
import logging
import os
import pickle
from datetime import datetime
from pytz import timezone
from shutil import rmtree
from tempfile import mkdtemp

from flask import (Blueprint, redirect, request,
                   render_template, session, url_for)
from sklearn.model_selection import train_test_split

from app import db
from app.core import evaluator, gatherer, util
from app.core.detection import Detector, classifiers_obj
from app.core.preprocessing import Extractor, Formatter, preprocessing_obj
from app.forms.setting import DatasetForm, ClassifierForm
from app.models import (Classifier, Dataset, Feature,
                        Model, Preprocessing, Result)


bp = Blueprint('setting', __name__)
logger = logging.getLogger('setting')


@bp.route('/load')
def load():
    files = util.directory_content(f'{util.paths["models"]}')[1]
    models = [Model.query.get(file.split('_')[0]) for file in files]

    return render_template('setting/load.html', models=models)


@bp.route('/dataset', methods=['GET', 'POST'])
def dataset():
    form = DatasetForm()
    form.datasets_choices()

    if request.method == 'POST' and form.validate_on_submit():
        logger.info(f'dataset: {form.dataset.data}, split: {form.split.data}, '
                    f'kfolds: {form.kfolds.data}')

        # parameters used when the dataset was created.
        details = form.dataset.data.split('_')
        dataset = Dataset(file=form.dataset.data,
                          window=details[1].split('w')[-1],
                          aggregation=details[2].split('t')[-1],
                          size=details[3].split('.csv')[0].split('s')[-1],
                          split=form.split.data,
                          kfolds=form.kfolds.data)
        db.session.add(dataset)
        db.session.commit()

        return redirect(url_for('setting.classifier'))
    return render_template('setting/dataset.html', form=form)


@bp.route('/classifier', methods=['GET', 'POST'])
def classifier():
    form = ClassifierForm()
    dataset = Dataset.query.all()[-1]

    if request.method == 'POST' and form.validate_on_submit():
        logger.info(f'preprocessing: {form.preprocessing.data}, '
                    f'classifiers: {form.classifiers.data[0]} '
                    f'features: {form.features.data}')
        session['last_models'] = list()

        for clf_pk in form.classifiers.data:
            clf = Classifier.query.get(clf_pk)
            pre = Preprocessing.query.get(form.preprocessing.data)
            dt = datetime.now(timezone('America/Sao_Paulo'))
            model = Model(file=' ',
                          datetime=dt,
                          dataset_id=dataset.id,
                          classifier_id=clf.id,
                          preprocessing_id=form.preprocessing.data)

            for feat_pk in form.features.data:
                model.features.append(Feature.query.get(feat_pk))
            db.session.add(model)
            db.session.commit()

            # committing the model to get the pk.
            model.file = (f'{model.id}_'
                          f'{"-".join(clf.name.lower().split(" "))}_'
                          f'{"-".join(pre.name.lower().split(" "))}_'
                          f'{dt.strftime("%Y%m%d%H%M%S")}')
            db.session.add(model)
            db.session.commit()

            session['last_models'].append(model.id)
            logger.info(f'last_models: {session["last_models"]}')

        return redirect(url_for('setting.result'))
    return render_template('setting/classifier.html', form=form)


@bp.route('/result', methods=['GET', 'POST'])
def result():
    models = [Model.query.get(model_pk) for model_pk in session['last_models']]
    dataset = Dataset.query.get(models[-1].dataset_id)

    # gathering flows.
    header, flows = gatherer.open_csv(f'{util.paths["csv"]}datasets/',
                                      dataset.file)
    logger.info(f'raw flow: {flows[0]}')

    # preprocessing flows.
    formatter = Formatter(gather=False, train=True)
    flows = formatter.format_flows(flows)
    logger.info(f'final flow: {flows[0]}')

    # extracting features.
    # adding extra value to skip first unused features.
    extractor = Extractor([feature.id+7 for feature in models[-1].features])
    features, labels = extractor.extract_features_labels(flows)
    logger.info(f'feature: {features[0]}, label: {labels[0]}')

    x_train, x_test, y_train, y_test = train_test_split(
        features, labels,
        test_size=dataset.split/100,
        stratify=labels)
    logger.info(f'x_train: {len(x_train)}')
    logger.info(f'x_test: {len(x_test)}')
    logger.info(f'y_train: {len(y_train)}')
    logger.info(f'y_test: {len(y_test)}')

    for model in models:
        # creating an absolute path of a temporary directory.
        cachedir = mkdtemp()
        preprocessing = Preprocessing.query.get(model.preprocessing_id)
        classifier = Classifier.query.get(model.classifier_id)
        prep_key = '_'.join(preprocessing.name.lower().split(' '))
        clf_key = '_'.join(classifier.name.lower().split(' '))
        logger.info(f'classifier: {classifier.name}')
        logger.info(f'preprocessing: {preprocessing.name}')

        # tunning, training and test.
        detector = Detector(copy.deepcopy(classifiers_obj[clf_key]))
        detector.define_tuning(copy.deepcopy(preprocessing_obj[prep_key]),
                               dataset.kfolds,
                               cachedir)

        hparam, train_date, train_dur = detector.train(x_train, y_train)
        pred, test_date, test_dur = detector.test(x_test)

        # results.
        outcome = evaluator.metrics(y_test, pred)
        result = Result(
            train_date=train_date, test_date=test_date,
            train_duration=train_dur, test_duration=test_dur,
            accuracy=outcome['accuracy'], precision=outcome['precision'],
            recall=outcome['recall'], f1_score=outcome['f1_score'],
            true_negative=outcome['tn'], false_positive=outcome['fp'],
            false_negative=outcome['fn'], true_positive=outcome['tp'],
            hyperparameters=str(hparam), model_id=model.id)
        db.session.add(result)
        db.session.commit()
        # removing the temporary directory used by the Pipeline object.
        rmtree(cachedir)
    columns = Model.__table__.columns

    return render_template('setting/result.html',
                           columns=columns,
                           models=models)


@bp.route('/model', methods=['GET', 'POST'])
def model():
    if request.method == 'POST':
        # creating an absolute path of a temporary directory
        tmp_directory = mkdtemp()
        model = Model.query.get(request.form['model_pk'])
        dataset = Dataset.query.get(model.dataset_id)
        preprocessing = Preprocessing.query.get(model.preprocessing_id)
        classifier = Classifier.query.get(model.classifier_id)
        prep_key = '_'.join(preprocessing.name.lower().split(' '))
        clf_key = '_'.join(classifier.name.lower().split(' '))
        logger.info(f'classifier: {classifier.name}')
        logger.info(f'preprocessing: {preprocessing.name}')

        # gathering flows.
        header, flows = gatherer.open_csv(f'{util.paths["csv"]}datasets/',
                                          dataset.file)
        session['last_models'].remove(model.id)
        logger.info(f'raw flow: {flows[0]}')

        # removing unselected models.
        for model_pk in session['last_models']:
            db.session.delete(Model.query.get(model_pk))
        db.session.commit()

        # preprocessing flows.
        formatter = Formatter(gather=False, train=True)
        flows = formatter.format_flows(flows)
        logger.info(f'final flow: {flows[0]}')

        # extracting features.
        # adding extra value to skip first unused features.
        extractor = Extractor([feature.id+7 for feature in model.features])
        features, labels = extractor.extract_features_labels(flows)
        logger.info(f'feature: {features[0]}, label: {labels[0]}')

        # tunning and retraining.
        detector = Detector(copy.deepcopy(classifiers_obj[clf_key]))
        detector.define_tuning(copy.deepcopy(preprocessing_obj[prep_key]),
                               dataset.kfolds,
                               tmp_directory)
        detector.retrain(features, labels)

        # model persistence.
        pickle.dump(detector,
                    open(f'{util.paths["models"]}{model.file}', 'wb'))
        logger.info(f'model file: {model.file}')
        # removing the temporary directory used by the Pipeline object.
        rmtree(tmp_directory)

    return redirect(url_for('setting.load'))
