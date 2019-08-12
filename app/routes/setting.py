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
from app.core import gatherer
from app.core import tools
from app.core.detection import Detector, classifiers_obj
from app.core.preprocess import Extractor, Formatter, preprocessing_obj
from app.forms.setting import LoadForm, DatasetForm, ClassifierForm
from app.models import (Classifier, Dataset, Feature,
                        Model, Preprocessing, Result)
from app.paths import paths


bp = Blueprint('setting', __name__)


@bp.route('/load')
def load():
    form = LoadForm()
    files = tools.get_content(f'{paths["models"]}')[1]
    return render_template('setting/load.html', form=form, files=files)


@bp.route('/dataset', methods=['GET', 'POST'])
def dataset():
    form = DatasetForm()
    form.dataset_choices()

    if request.method == 'POST' and form.validate_on_submit():
        # parameters used when the dataset was created
        details = form.dataset.data.split('_')
        dataset = Dataset(file=form.dataset.data,
                          window=details[1].split('w')[-1],
                          aggregation=details[2].split('a')[-1],
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
    # removing some features if dataset is not aggregated
    dataset = Dataset.query.all()[-1]

    if not dataset.aggregation:
        form.features.choices = form.features.choices[2:8]

    if request.method == 'POST' and form.validate_on_submit():
        session['last_models'] = list()

        for clf_pk in form.classifiers.data:
            clf = Classifier.query.get(clf_pk)
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
            # committing the model first in order to get the pk
            model.file = (f'{model.id}_'
                          f'{"_".join(clf.name.lower().split(" "))}_'
                          f'{dt.strftime("%Y%m%d%H%M%S")}')
            db.session.add(model)
            db.session.commit()
            # session used to remember the pk of the latest models
            session['last_models'].append(model.id)
        return redirect(url_for('setting.result'))
    return render_template('setting/classifier.html', form=form)


@bp.route('/result', methods=['GET', 'POST'])
def result():
    # creating an absolute path of a temporary directory
    tmp_directory = mkdtemp()
    # chosen models
    models = [Model.query.get(model_pk) for model_pk in session['last_models']]
    dataset = Dataset.query.get(models[-1].dataset_id)
    header, flows = gatherer.open_csv(f'{paths["csv"]}datasets/', dataset.file)

    # data formatting
    for entry in flows:
        Formatter.convert_features(entry, True)

    # data extraction
    # adding extra value to skip first unused features
    extractor = Extractor([feature.id+5 for feature in models[-1].features])
    features, labels = extractor.extract_features(flows)

    x_train, x_test, y_train, y_test = train_test_split(
        features, labels,
        test_size=dataset.split,
        stratify=labels)

    for model in models:
        classifier = Classifier.query.get(model.classifier_id)
        preprocessing = Preprocessing.query.get(model.preprocessing_id)
        detector = Detector(
            classifiers_obj['_'.join(classifier.name.lower().split(' '))])

        detector.define_tuning(
            preprocessing_obj['_'.join(preprocessing.name.lower().split(' '))],
            dataset.kfolds,
            tmp_directory)
        # training
        hparam, train_date, train_dur = detector.train(x_train, y_train)
        # test
        pred, test_date, test_dur = detector.test(x_test)
        outcome = tools.evaluation_metrics(y_test, pred)

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
    # removing the temporary directory used by the Pipeline object
    rmtree(tmp_directory)

    return render_template('setting/result.html', models=models)


@bp.route('/model', methods=['GET', 'POST'])
def model():
    if request.method == 'POST':
        # creating an absolute path of a temporary directory
        tmp_directory = mkdtemp()
        model = Model.query.get(request.form['model_pk'])
        dataset = Dataset.query.get(model.dataset_id)
        classifier = Classifier.query.get(model.classifier_id)
        preprocessing = Preprocessing.query.get(model.preprocessing_id)
        header, flows = gatherer.open_csv(f'{paths["csv"]}datasets/',
                                          dataset.file)
        session['last_models'].remove(model.id)

        # removing unselected models
        for model_pk in session['last_models']:
            db.session.delete(Model.query.get(model_pk))
        db.session.commit()

        # data formatting
        for entry in flows:
            Formatter.convert_features(entry, True)

        # data extraction
        # adding extra value to skip first unused features
        extractor = Extractor([feature.id+5 for feature in model.features])
        features, labels = extractor.extract_features(flows)
        detector = Detector(
            classifiers_obj['_'.join(classifier.name.lower().split(' '))])

        detector.define_tuning(
            preprocessing_obj['_'.join(preprocessing.name.lower().split(' '))],
            dataset.kfolds,
            tmp_directory)
        # retraining
        detector.train(features, labels)
        # model persistence
        pickle.dump(detector, open(f'{paths["models"]}{model.file}', 'wb'))
        # removing the temporary directory used by the Pipeline object
        rmtree(tmp_directory)

    return redirect(url_for('detection.realtime'))
